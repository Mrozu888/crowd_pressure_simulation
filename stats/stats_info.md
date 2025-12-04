Interpretacja panelu statystyk (HUD)

t, agents
---------
t – czas symulacji od startu [s].
agents – liczba aktywnych agentów w scenie (ci, którzy jeszcze nie wyszli).

Zones
-----
store  – ilu agentów aktualnie znajduje się w sali sprzedaży (wewnątrz sklepu).
vest   – ilu agentów jest w wiatrołapie (vestibule).
street – ilu agentów jest na zewnątrz (ulica / przed wejściem).

Flow [people/min]
-----------------
left  – przepływ przez lewe drzwi (ulica ↔ wiatrołap) w osobach na minutę,
        liczony w ruchomym oknie czasowym (np. 60 s).
top   – przepływ przez górne drzwi (wiatrołap ↔ sala sprzedaży).
right – przepływ przez prawe drzwi (sala sprzedaży ↔ wiatrołap/wyjście).

Contacts
--------
d<1m     – liczba zdarzeń, w których odległość między parą agentów była < 1 m.
d<covid – liczba zdarzeń, w których odległość była mniejsza niż dystans
          zadany dla trybu COVID (np. 1.5–2.0 m).

Speed
-----
avg   – średnia prędkość wszystkich agentów [m/s].
store – średnia prędkość tylko w strefie sklepu.
vest  – średnia prędkość tylko w strefie wiatrołapu.

Queue front cashiers
--------------------
Aktualna liczba agentów znajdujących się w zdefiniowanym prostokącie
„przed kasami”, czyli w strefie kolejki do kas.

Density
-------
store – średnia gęstość w sali sprzedaży [osób/m²].
vest  – średnia gęstość w wiatrołapie [osób/m²].
