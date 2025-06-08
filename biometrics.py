import cv2
import numpy as np
import hashlib
import os
import sqlite3
import json
from cryptography.fernet import Fernet
import base64

DB_PATH = "secure_face.db"
STATIC_KEY = hashlib.sha256(b"moje_tajne_haslo_123").digest()
FERNET_KEY = base64.urlsafe_b64encode(STATIC_KEY[:32])
fernet = Fernet(FERNET_KEY)

# --- Baza danych ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS biometrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ratios TEXT NOT NULL,
            key TEXT NOT NULL
        );
    ''')
    conn.commit()
    return conn

def save_multiple_reference_data_sqlite(scans):
    conn = init_db()
    cursor = conn.cursor()
    scans_serialized = json.dumps([scan.tolist() for scan in scans])
    hash_key = generate_biometric_key(scans[0])
    enc_scans = fernet.encrypt(scans_serialized.encode()).decode()
    enc_key = fernet.encrypt(hash_key.encode()).decode()
    cursor.execute("DELETE FROM biometrics")
    cursor.execute("INSERT INTO biometrics (ratios, key) VALUES (?, ?)", (enc_scans, enc_key))
    conn.commit()
    conn.close()

def load_reference_data_sqlite():
    if not os.path.exists(DB_PATH):
        return None, None
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ratios, key FROM biometrics LIMIT 1;")
    row = cursor.fetchone()
    conn.close()
    if row:
        ratios = np.array(json.loads(fernet.decrypt(row[0].encode()).decode()), dtype=np.float32)
        key = fernet.decrypt(row[1].encode()).decode()
        return ratios, key
    return None, None

# --- Detekcja twarzy i landmarków ---
def detect_landmarks(image, face_detector, landmark_detector):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    landmarks_list = []
    face_rects = [(x, y, w, h) for (x, y, w, h) in faces]

    if face_rects:
        ok, landmarks = landmark_detector.fit(gray, np.array(face_rects))
        if ok:
            for shape in landmarks:
                landmarks_list.append([tuple(pt) for pt in shape[0]])

    return faces, landmarks_list

def get_landmark_ratios(landmarks):
    LEFT_EYE = [36, 37, 38, 39, 40, 41]
    RIGHT_EYE = [42, 43, 44, 45, 46, 47]
    NOSE_TIP = 30
    MOUTH_LEFT = 48
    MOUTH_RIGHT = 54

    left_eye_center = np.mean([landmarks[i] for i in LEFT_EYE], axis=0)
    right_eye_center = np.mean([landmarks[i] for i in RIGHT_EYE], axis=0)

    eye_distance = np.linalg.norm(left_eye_center - right_eye_center)
    nose_to_mouth = np.linalg.norm(
        np.array(landmarks[NOSE_TIP]) - np.mean([landmarks[MOUTH_LEFT], landmarks[MOUTH_RIGHT]], axis=0)
    )

    ratios = [
        eye_distance / nose_to_mouth,
        eye_distance / np.linalg.norm(
            np.array(landmarks[MOUTH_LEFT]) - np.array(landmarks[MOUTH_RIGHT])
        )
    ]

    return np.array(ratios, dtype=np.float32)

def generate_biometric_key(ratios, precision=4):
    rounded = np.round(ratios, decimals=precision)
    ratios_str = "|".join(f"{x:.{precision}f}" for x in rounded)
    return hashlib.sha256(ratios_str.encode('utf-8')).hexdigest()

# --- Funkcje główne ---
import time
import cv2
import numpy as np

def scan_face_multiple_times(count=4):
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    landmark_detector = cv2.face.createFacemarkLBF()
    landmark_detector.loadModel("lbfmodel.yaml")

    cam = cv2.VideoCapture(0)
    scans = []

    while len(scans) < count:
        ret, frame = cam.read()
        if not ret:
            continue

        faces, landmarks_list = detect_landmarks(frame, face_detector, landmark_detector)

        # Rysuj zielony prostokąt i czerwone punkty
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        for landmarks in landmarks_list:
            for (lx, ly) in landmarks:
                cv2.circle(frame, (int(lx), int(ly)), 2, (0, 0, 255), -1)

        if landmarks_list:
            # Odliczanie w czasie rzeczywistym (3 sekundy)
            start_time = time.time()
            countdown_duration = 3.0
            while True:
                ret2, frame2 = cam.read()
                if not ret2:
                    continue

                faces2, landmarks_list2 = detect_landmarks(frame2, face_detector, landmark_detector)
                for (x, y, w, h) in faces2:
                    cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)
                for landmarks2 in landmarks_list2:
                    for (lx, ly) in landmarks2:
                        cv2.circle(frame2, (int(lx), int(ly)), 2, (0, 0, 255), -1)

                elapsed = time.time() - start_time
                remaining = max(0, countdown_duration - elapsed)
                cv2.putText(frame2, f"Uloz sie... {int(remaining)+1}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
                cv2.imshow("Skanowanie twarzy", frame2)

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    cam.release()
                    cv2.destroyAllWindows()
                    return scans

                if elapsed >= countdown_duration:
                    break

            # Po odliczaniu zbieramy dane z ostatniej klatki
            ratios = get_landmark_ratios(landmarks_list[0])
            scans.append(ratios)
            print(f"Skan {len(scans)} wykonany: {ratios}")
        else:
            cv2.putText(frame, "Nie wykryto twarzy", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            cv2.imshow("Skanowanie twarzy", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    return scans


def recognize_face(tolerance=0.08):
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    landmark_detector = cv2.face.createFacemarkLBF()
    landmark_detector.loadModel("lbfmodel.yaml")

    reference_scans, reference_key = load_reference_data_sqlite()
    if reference_scans is None:
        print("❌ Brak danych biometrycznych. Zeskanuj twarz najpierw.")
        return False, None

    cam = cv2.VideoCapture(0)
    recognized = False
    while True:
        ret, frame = cam.read()
        if not ret:
            continue
        faces, landmarks_list = detect_landmarks(frame, face_detector, landmark_detector)
        if landmarks_list:
            current_ratios = get_landmark_ratios(landmarks_list[0])
            distances = [np.linalg.norm(current_ratios - r) for r in reference_scans]
            min_dist = min(distances)
            print(f"Odchylenie: {min_dist:.5f}")
            if min_dist < tolerance:
                print("✅ Twarz rozpoznana")
                recognized = True
                break
            else:
                print("❌ Brak zgodności biometrycznej")
        cv2.imshow("Rozpoznawanie twarzy", frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    return recognized, reference_key
