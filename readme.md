# Opis projektu: Bezpieczny system szyfrowania plików z uwierzytelnianiem biometrycznym twarzy

## 1. Sformułowanie problemu  
W dobie rosnącej cyfryzacji bezpieczeństwo danych osobowych i firmowych stanowi priorytet. Tradycyjne metody zabezpieczeń, takie jak hasła, są często podatne na wycieki, kradzieże lub zapomnienie. Celem projektu jest stworzenie systemu umożliwiającego szyfrowanie i odszyfrowywanie plików z wykorzystaniem unikalnych cech biometrycznych twarzy użytkownika jako klucza dostępu. Projekt ma na celu podniesienie poziomu bezpieczeństwa danych poprzez eliminację potrzeby stosowania tradycyjnych haseł.

## 2. Opis zastosowanej metody  
Projekt wykorzystuje techniki przetwarzania obrazu do wykrywania i analizy twarzy użytkownika, w szczególności detekcję punktów charakterystycznych (landmarków) na twarzy. Na podstawie odległości i proporcji pomiędzy kluczowymi punktami twarzy generowany jest unikalny klucz biometryczny. Ten klucz jest następnie używany do symetrycznego szyfrowania plików przy pomocy algorytmu Fernet (z biblioteki cryptography), zapewniając poufność i integralność danych. Dane biometryczne oraz klucz szyfrujący są przechowywane w zaszyfrowanej bazie danych SQLite z użyciem pysqlcipher3.

## 3. Implementacja  
Projekt został zaimplementowany w języku Python z wykorzystaniem następujących narzędzi i bibliotek:  
- OpenCV (cv2) do detekcji twarzy i punktów charakterystycznych,  
- pysqlcipher3 do bezpiecznego zarządzania zaszyfrowaną bazą danych,  
- cryptography (Fernet) do szyfrowania i odszyfrowywania plików,  
- tkinter oraz tkinterdnd2 do stworzenia graficznego interfejsu użytkownika umożliwiającego przeciąganie i upuszczanie plików,  
- wbudowane mechanizmy bezpieczeństwa do generowania i ochrony kluczy szyfrujących na podstawie cech biometrycznych.

Kod jest podzielony na moduły odpowiedzialne za skanowanie twarzy, rozpoznawanie, zarządzanie bazą, oraz szyfrowanie plików, co zapewnia modularność i czytelność.

## 4. Prezentacja wyników  
- System umożliwia wielokrotne skanowanie twarzy w celu wygenerowania stabilnego wzorca biometrycznego.  
- Po poprawnej rejestracji i rozpoznaniu twarzy użytkownik może przeciągać pliki do aplikacji, które są automatycznie szyfrowane lub odszyfrowywane na podstawie biometrycznego klucza.  
- Interfejs użytkownika pokazuje status operacji, informując o sukcesie lub błędach.  
- W testach wykazano skuteczność rozpoznawania z tolerancją odległościową 0.08 oraz stabilność szyfrowania i odszyfrowywania danych.  
- Kod źródłowy oraz logika działania dostępne są w repozytorium projektu, umożliwiając łatwą analizę i rozbudowę.

## 5. Możliwe rozszerzenia/kontynuacja projektu  
- Implementacja rozpoznawania twarzy z użyciem bardziej zaawansowanych sieci neuronowych (np. deep learning), co zwiększy dokładność i odporność na zmienne warunki oświetleniowe.  
- Dodanie wieloużytkownikowego systemu zarządzania biometrią z możliwością rejestracji i autoryzacji wielu osób.  
- Integracja z chmurą do bezpiecznego przechowywania zaszyfrowanych plików oraz synchronizacji między urządzeniami.  
- Rozbudowa interfejsu o obsługę innych formatów plików i możliwość masowego szyfrowania.  
- Wprowadzenie mechanizmów audytu i monitoringu próby dostępu, a także powiadomień o nieudanych próbach rozpoznania twarzy.  
- Zastosowanie innych metod biometrycznych (np. odcisk palca, skan tęczówki) jako alternatywnych metod uwierzytelniania.
