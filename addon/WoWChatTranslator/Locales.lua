local _, ns = ...

-- Minimal localisation table, English is the fallback.
local L = {
    enUS = {
        RELOAD_PROMPT = "The chat position has changed. Reload the interface so the translation lines up with your chat?",
        RELOAD = "Reload",
        LATER = "Later",
        BRIDGE_ON = "Bridge to the companion: |cff00ff00active|r (%d message(s) waiting)",
        TEST_SENT = "Test message sent to the companion.",
        HELP = "Commands: /wct (status), /wct on (start), /wct test (test message), /wct pos (re-sync chat position), /wct toggle (show/hide)",
        COMPANION_OFF = "Companion not detected: translation off. Start WoWChatTranslatorCompagnion, then type /wct on.",
        BINDING_TOGGLE = "Show / hide the translation overlay",
        BINDING_SCREENSHOT = "Screenshot with the translation overlay",
        SCREENSHOT_OFF = "No translation overlay: screenshot not possible.",
        OVERLAY_HIDDEN = "Translation overlay hidden (%s or /wct toggle to show it).",
        OVERLAY_HIDDEN_NOKEY = "Translation overlay hidden (/wct toggle to show it).",
        OVERLAY_SHOWN = "Translation overlay shown.",
    },
    frFR = {
        RELOAD_PROMPT = "La position du chat a changé. Recharger l'interface pour caler la traduction sur votre chat ?",
        RELOAD = "Recharger",
        LATER = "Plus tard",
        BRIDGE_ON = "Pont vers le compagnon : |cff00ff00actif|r (%d message(s) en attente)",
        TEST_SENT = "Message de test envoyé au compagnon.",
        HELP = "Commandes : /wct (état), /wct on (activer), /wct test (message de test), /wct pos (recaler la position du chat), /wct toggle (afficher/masquer)",
        COMPANION_OFF = "Compagnon non détecté : traduction désactivée. Lancez WoWChatTranslatorCompagnion puis tapez /wct on.",
        BINDING_TOGGLE = "Afficher / masquer la surcouche de traduction",
        BINDING_SCREENSHOT = "Capture d'écran avec la surcouche de traduction",
        SCREENSHOT_OFF = "Surcouche de traduction absente : capture impossible.",
        OVERLAY_HIDDEN = "Surcouche de traduction masquée (%s ou /wct toggle pour l'afficher).",
        OVERLAY_HIDDEN_NOKEY = "Surcouche de traduction masquée (/wct toggle pour l'afficher).",
        OVERLAY_SHOWN = "Surcouche de traduction affichée.",
    },
    deDE = {
        RELOAD_PROMPT = "Die Chatposition hat sich geändert. Oberfläche neu laden, damit die Übersetzung auf deinem Chat liegt?",
        RELOAD = "Neu laden",
        LATER = "Später",
        BRIDGE_ON = "Brücke zum Begleiter: |cff00ff00aktiv|r (%d Nachricht(en) wartend)",
        TEST_SENT = "Testnachricht an den Begleiter gesendet.",
        HELP = "Befehle: /wct (Status), /wct test (Testnachricht), /wct pos (Chatposition abgleichen), /wct toggle (ein-/ausblenden)",
        COMPANION_OFF = "Begleiter nicht erkannt: Übersetzung aus. Starte WoWChatTranslatorCompagnion und gib /wct on ein.",
        BINDING_TOGGLE = "Übersetzungsoverlay ein-/ausblenden",
        BINDING_SCREENSHOT = "Screenshot mit dem Übersetzungsoverlay",
        SCREENSHOT_OFF = "Kein Übersetzungsoverlay: Screenshot nicht möglich.",
        OVERLAY_HIDDEN = "Übersetzungsoverlay ausgeblendet (%s oder /wct toggle zum Einblenden).",
        OVERLAY_HIDDEN_NOKEY = "Übersetzungsoverlay ausgeblendet (/wct toggle zum Einblenden).",
        OVERLAY_SHOWN = "Übersetzungsoverlay eingeblendet.",
    },
    esES = {
        RELOAD_PROMPT = "La posición del chat ha cambiado. ¿Recargar la interfaz para alinear la traducción con tu chat?",
        RELOAD = "Recargar",
        LATER = "Más tarde",
        BRIDGE_ON = "Puente al compañero: |cff00ff00activo|r (%d mensaje(s) en espera)",
        TEST_SENT = "Mensaje de prueba enviado al compañero.",
        HELP = "Comandos: /wct (estado), /wct test (mensaje de prueba), /wct pos (reajustar la posición del chat), /wct toggle (mostrar/ocultar)",
        COMPANION_OFF = "Compañero no detectado: traducción desactivada. Inicia WoWChatTranslatorCompagnion y escribe /wct on.",
        BINDING_TOGGLE = "Mostrar / ocultar la capa de traducción",
        BINDING_SCREENSHOT = "Captura de pantalla con la capa de traducción",
        SCREENSHOT_OFF = "Sin capa de traducción: captura imposible.",
        OVERLAY_HIDDEN = "Capa de traducción oculta (%s o /wct toggle para mostrarla).",
        OVERLAY_HIDDEN_NOKEY = "Capa de traducción oculta (/wct toggle para mostrarla).",
        OVERLAY_SHOWN = "Capa de traducción visible.",
    },
    itIT = {
        RELOAD_PROMPT = "La posizione della chat è cambiata. Ricaricare l'interfaccia per allineare la traduzione alla chat?",
        RELOAD = "Ricarica",
        LATER = "Più tardi",
        BRIDGE_ON = "Ponte verso il compagno: |cff00ff00attivo|r (%d messaggio/i in attesa)",
        TEST_SENT = "Messaggio di prova inviato al compagno.",
        HELP = "Comandi: /wct (stato), /wct test (messaggio di prova), /wct pos (riallinea la posizione della chat), /wct toggle (mostra/nascondi)",
        COMPANION_OFF = "Compagno non rilevato: traduzione disattivata. Avvia WoWChatTranslatorCompagnion e digita /wct on.",
        BINDING_TOGGLE = "Mostra / nascondi il livello di traduzione",
        BINDING_SCREENSHOT = "Screenshot con il livello di traduzione",
        SCREENSHOT_OFF = "Nessun livello di traduzione: screenshot impossibile.",
        OVERLAY_HIDDEN = "Livello di traduzione nascosto (%s o /wct toggle per mostrarlo).",
        OVERLAY_HIDDEN_NOKEY = "Livello di traduzione nascosto (/wct toggle per mostrarlo).",
        OVERLAY_SHOWN = "Livello di traduzione visibile.",
    },
    ptBR = {
        RELOAD_PROMPT = "A posição do chat mudou. Recarregar a interface para alinhar a tradução ao seu chat?",
        RELOAD = "Recarregar",
        LATER = "Mais tarde",
        BRIDGE_ON = "Ponte para o companheiro: |cff00ff00ativa|r (%d mensagem(ns) em espera)",
        TEST_SENT = "Mensagem de teste enviada ao companheiro.",
        HELP = "Comandos: /wct (estado), /wct test (mensagem de teste), /wct pos (reajustar a posição do chat), /wct toggle (mostrar/ocultar)",
        COMPANION_OFF = "Companheiro não detectado: tradução desativada. Inicie o WoWChatTranslatorCompagnion e digite /wct on.",
        BINDING_TOGGLE = "Mostrar / ocultar a camada de tradução",
        BINDING_SCREENSHOT = "Captura de tela com a camada de tradução",
        SCREENSHOT_OFF = "Sem camada de tradução: captura impossível.",
        OVERLAY_HIDDEN = "Camada de tradução oculta (%s ou /wct toggle para mostrá-la).",
        OVERLAY_HIDDEN_NOKEY = "Camada de tradução oculta (/wct toggle para mostrá-la).",
        OVERLAY_SHOWN = "Camada de tradução visível.",
    },
    ruRU = {
        RELOAD_PROMPT = "Положение чата изменилось. Перезагрузить интерфейс, чтобы перевод совпал с чатом?",
        RELOAD = "Перезагрузить",
        LATER = "Позже",
        BRIDGE_ON = "Мост к компаньону: |cff00ff00активен|r (сообщений в очереди: %d)",
        TEST_SENT = "Тестовое сообщение отправлено компаньону.",
        HELP = "Команды: /wct (состояние), /wct test (тестовое сообщение), /wct pos (выровнять положение чата), /wct toggle (показать/скрыть)",
        COMPANION_OFF = "Компаньон не найден: перевод выключен. Запустите WoWChatTranslatorCompagnion и введите /wct on.",
        BINDING_TOGGLE = "Показать / скрыть слой перевода",
        BINDING_SCREENSHOT = "Снимок экрана со слоем перевода",
        SCREENSHOT_OFF = "Нет слоя перевода: снимок невозможен.",
        OVERLAY_HIDDEN = "Слой перевода скрыт (%s или /wct toggle, чтобы показать).",
        OVERLAY_HIDDEN_NOKEY = "Слой перевода скрыт (/wct toggle, чтобы показать).",
        OVERLAY_SHOWN = "Слой перевода показан.",
    },
    -- Reading languages without a WoW client: chosen in the companion (Companion.lua).
    pl = {
        RELOAD_PROMPT = "Pozycja czatu się zmieniła. Przeładować interfejs, aby tłumaczenie pasowało do czatu?",
        RELOAD = "Przeładuj",
        LATER = "Później",
        BRIDGE_ON = "Most do towarzysza: |cff00ff00aktywny|r (%d wiadomości w kolejce)",
        TEST_SENT = "Wiadomość testowa wysłana do towarzysza.",
        HELP = "Polecenia: /wct (stan), /wct on (włącz), /wct test (wiadomość testowa), /wct pos (wyrównaj pozycję czatu), /wct toggle (pokaż/ukryj)",
        COMPANION_OFF = "Nie wykryto towarzysza: tłumaczenie wyłączone. Uruchom WoWChatTranslatorCompagnion, potem wpisz /wct on.",
        BINDING_TOGGLE = "Pokaż / ukryj nakładkę tłumaczenia",
        BINDING_SCREENSHOT = "Zrzut ekranu z nakładką tłumaczenia",
        SCREENSHOT_OFF = "Brak nakładki tłumaczenia: zrzut niemożliwy.",
        OVERLAY_HIDDEN = "Nakładka tłumaczenia ukryta (%s lub /wct toggle, aby pokazać).",
        OVERLAY_HIDDEN_NOKEY = "Nakładka tłumaczenia ukryta (/wct toggle, aby pokazać).",
        OVERLAY_SHOWN = "Nakładka tłumaczenia pokazana.",
    },
    nl = {
        RELOAD_PROMPT = "De positie van de chat is gewijzigd. De interface herladen zodat de vertaling bij je chat past?",
        RELOAD = "Herladen",
        LATER = "Later",
        BRIDGE_ON = "Brug naar de companion: |cff00ff00actief|r (%d bericht(en) in wachtrij)",
        TEST_SENT = "Testbericht naar de companion gestuurd.",
        HELP = "Commando's: /wct (status), /wct on (starten), /wct test (testbericht), /wct pos (chatpositie opnieuw instellen), /wct toggle (tonen/verbergen)",
        COMPANION_OFF = "Companion niet gevonden: vertaling uit. Start WoWChatTranslatorCompagnion en typ daarna /wct on.",
        BINDING_TOGGLE = "Vertaaloverlay tonen / verbergen",
        BINDING_SCREENSHOT = "Schermafbeelding met de vertaaloverlay",
        SCREENSHOT_OFF = "Geen vertaaloverlay: schermafbeelding niet mogelijk.",
        OVERLAY_HIDDEN = "Vertaaloverlay verborgen (%s of /wct toggle om te tonen).",
        OVERLAY_HIDDEN_NOKEY = "Vertaaloverlay verborgen (/wct toggle om te tonen).",
        OVERLAY_SHOWN = "Vertaaloverlay getoond.",
    },
    sv = {
        RELOAD_PROMPT = "Chattens position har ändrats. Ladda om gränssnittet så att översättningen hamnar rätt över chatten?",
        RELOAD = "Ladda om",
        LATER = "Senare",
        BRIDGE_ON = "Brygga till följeslagaren: |cff00ff00aktiv|r (%d meddelande(n) i kö)",
        TEST_SENT = "Testmeddelande skickat till följeslagaren.",
        HELP = "Kommandon: /wct (status), /wct on (starta), /wct test (testmeddelande), /wct pos (justera chattens position), /wct toggle (visa/dölj)",
        COMPANION_OFF = "Följeslagaren hittades inte: översättningen är av. Starta WoWChatTranslatorCompagnion och skriv sedan /wct on.",
        BINDING_TOGGLE = "Visa / dölj översättningsöverlägget",
        BINDING_SCREENSHOT = "Skärmbild med översättningsöverlägget",
        SCREENSHOT_OFF = "Inget översättningsöverlägg: skärmbild inte möjlig.",
        OVERLAY_HIDDEN = "Översättningsöverlägget dolt (%s eller /wct toggle för att visa).",
        OVERLAY_HIDDEN_NOKEY = "Översättningsöverlägget dolt (/wct toggle för att visa).",
        OVERLAY_SHOWN = "Översättningsöverlägget visas.",
    },
    da = {
        RELOAD_PROMPT = "Chattens position er ændret. Genindlæs brugerfladen, så oversættelsen passer til din chat?",
        RELOAD = "Genindlæs",
        LATER = "Senere",
        BRIDGE_ON = "Bro til ledsageren: |cff00ff00aktiv|r (%d besked(er) i kø)",
        TEST_SENT = "Testbesked sendt til ledsageren.",
        HELP = "Kommandoer: /wct (status), /wct on (start), /wct test (testbesked), /wct pos (juster chattens position), /wct toggle (vis/skjul)",
        COMPANION_OFF = "Ledsageren blev ikke fundet: oversættelse slået fra. Start WoWChatTranslatorCompagnion, og skriv derefter /wct on.",
        BINDING_TOGGLE = "Vis / skjul oversættelsesoverlejringen",
        BINDING_SCREENSHOT = "Skærmbillede med oversættelsesoverlejringen",
        SCREENSHOT_OFF = "Ingen oversættelsesoverlejring: skærmbillede ikke muligt.",
        OVERLAY_HIDDEN = "Oversættelsesoverlejringen er skjult (%s eller /wct toggle for at vise den).",
        OVERLAY_HIDDEN_NOKEY = "Oversættelsesoverlejringen er skjult (/wct toggle for at vise den).",
        OVERLAY_SHOWN = "Oversættelsesoverlejringen vises.",
    },
    no = {
        RELOAD_PROMPT = "Chatens posisjon er endret. Laste inn grensesnittet på nytt slik at oversettelsen passer til chatten?",
        RELOAD = "Last inn på nytt",
        LATER = "Senere",
        BRIDGE_ON = "Bro til følgesvennen: |cff00ff00aktiv|r (%d melding(er) i kø)",
        TEST_SENT = "Testmelding sendt til følgesvennen.",
        HELP = "Kommandoer: /wct (status), /wct on (start), /wct test (testmelding), /wct pos (juster chatens posisjon), /wct toggle (vis/skjul)",
        COMPANION_OFF = "Fant ikke følgesvennen: oversettelse av. Start WoWChatTranslatorCompagnion, og skriv deretter /wct on.",
        BINDING_TOGGLE = "Vis / skjul oversettelsesoverlegget",
        BINDING_SCREENSHOT = "Skjermbilde med oversettelsesoverlegget",
        SCREENSHOT_OFF = "Ikke noe oversettelsesoverlegg: skjermbilde ikke mulig.",
        OVERLAY_HIDDEN = "Oversettelsesoverlegget er skjult (%s eller /wct toggle for å vise det).",
        OVERLAY_HIDDEN_NOKEY = "Oversettelsesoverlegget er skjult (/wct toggle for å vise det).",
        OVERLAY_SHOWN = "Oversettelsesoverlegget vises.",
    },
    fi = {
        RELOAD_PROMPT = "Chatin sijainti on muuttunut. Ladataanko käyttöliittymä uudelleen, jotta käännös osuu chatin kohdalle?",
        RELOAD = "Lataa uudelleen",
        LATER = "Myöhemmin",
        BRIDGE_ON = "Silta kumppanisovellukseen: |cff00ff00käytössä|r (%d viesti(ä) jonossa)",
        TEST_SENT = "Testiviesti lähetetty kumppanisovellukselle.",
        HELP = "Komennot: /wct (tila), /wct on (käynnistä), /wct test (testiviesti), /wct pos (kohdista chatin sijainti), /wct toggle (näytä/piilota)",
        COMPANION_OFF = "Kumppanisovellusta ei löytynyt: käännös pois päältä. Käynnistä WoWChatTranslatorCompagnion ja kirjoita sitten /wct on.",
        BINDING_TOGGLE = "Näytä / piilota käännöksen peitekerros",
        BINDING_SCREENSHOT = "Kuvakaappaus käännöksen peitekerroksen kanssa",
        SCREENSHOT_OFF = "Ei käännöksen peitekerrosta: kuvakaappaus ei onnistu.",
        OVERLAY_HIDDEN = "Käännöksen peitekerros piilotettu (%s tai /wct toggle näyttää sen).",
        OVERLAY_HIDDEN_NOKEY = "Käännöksen peitekerros piilotettu (/wct toggle näyttää sen).",
        OVERLAY_SHOWN = "Käännöksen peitekerros näkyvissä.",
    },
    cs = {
        RELOAD_PROMPT = "Pozice chatu se změnila. Znovu načíst rozhraní, aby překlad seděl na chat?",
        RELOAD = "Znovu načíst",
        LATER = "Později",
        BRIDGE_ON = "Most ke společníkovi: |cff00ff00aktivní|r (%d zpráv ve frontě)",
        TEST_SENT = "Testovací zpráva odeslána společníkovi.",
        HELP = "Příkazy: /wct (stav), /wct on (zapnout), /wct test (testovací zpráva), /wct pos (srovnat pozici chatu), /wct toggle (zobrazit/skrýt)",
        COMPANION_OFF = "Společník nebyl nalezen: překlad vypnut. Spusťte WoWChatTranslatorCompagnion a pak napište /wct on.",
        BINDING_TOGGLE = "Zobrazit / skrýt překladovou vrstvu",
        BINDING_SCREENSHOT = "Snímek obrazovky s překladovou vrstvou",
        SCREENSHOT_OFF = "Žádná překladová vrstva: snímek není možný.",
        OVERLAY_HIDDEN = "Překladová vrstva skryta (%s nebo /wct toggle pro zobrazení).",
        OVERLAY_HIDDEN_NOKEY = "Překladová vrstva skryta (/wct toggle pro zobrazení).",
        OVERLAY_SHOWN = "Překladová vrstva zobrazena.",
    },
    sk = {
        RELOAD_PROMPT = "Pozícia chatu sa zmenila. Znova načítať rozhranie, aby preklad sedel na chat?",
        RELOAD = "Znova načítať",
        LATER = "Neskôr",
        BRIDGE_ON = "Most k spoločníkovi: |cff00ff00aktívny|r (%d správ v poradí)",
        TEST_SENT = "Testovacia správa odoslaná spoločníkovi.",
        HELP = "Príkazy: /wct (stav), /wct on (zapnúť), /wct test (testovacia správa), /wct pos (zarovnať pozíciu chatu), /wct toggle (zobraziť/skryť)",
        COMPANION_OFF = "Spoločník sa nenašiel: preklad vypnutý. Spustite WoWChatTranslatorCompagnion a potom napíšte /wct on.",
        BINDING_TOGGLE = "Zobraziť / skryť prekladovú vrstvu",
        BINDING_SCREENSHOT = "Snímka obrazovky s prekladovou vrstvou",
        SCREENSHOT_OFF = "Žiadna prekladová vrstva: snímka nie je možná.",
        OVERLAY_HIDDEN = "Prekladová vrstva skrytá (%s alebo /wct toggle na zobrazenie).",
        OVERLAY_HIDDEN_NOKEY = "Prekladová vrstva skrytá (/wct toggle na zobrazenie).",
        OVERLAY_SHOWN = "Prekladová vrstva zobrazená.",
    },
    ro = {
        RELOAD_PROMPT = "Poziția chatului s-a schimbat. Reîncarci interfața ca traducerea să se potrivească pe chat?",
        RELOAD = "Reîncarcă",
        LATER = "Mai târziu",
        BRIDGE_ON = "Punte către însoțitor: |cff00ff00activă|r (%d mesaj(e) în așteptare)",
        TEST_SENT = "Mesaj de test trimis însoțitorului.",
        HELP = "Comenzi: /wct (stare), /wct on (pornește), /wct test (mesaj de test), /wct pos (realiniază poziția chatului), /wct toggle (arată/ascunde)",
        COMPANION_OFF = "Însoțitorul nu a fost detectat: traducere oprită. Pornește WoWChatTranslatorCompagnion, apoi scrie /wct on.",
        BINDING_TOGGLE = "Arată / ascunde stratul de traducere",
        BINDING_SCREENSHOT = "Captură de ecran cu stratul de traducere",
        SCREENSHOT_OFF = "Niciun strat de traducere: captură imposibilă.",
        OVERLAY_HIDDEN = "Stratul de traducere este ascuns (%s sau /wct toggle pentru a-l afișa).",
        OVERLAY_HIDDEN_NOKEY = "Stratul de traducere este ascuns (/wct toggle pentru a-l afișa).",
        OVERLAY_SHOWN = "Stratul de traducere este afișat.",
    },
    hu = {
        RELOAD_PROMPT = "A chat helyzete megváltozott. Újratöltöd a felületet, hogy a fordítás a chatre illeszkedjen?",
        RELOAD = "Újratöltés",
        LATER = "Később",
        BRIDGE_ON = "Híd a kísérőprogramhoz: |cff00ff00aktív|r (%d üzenet vár)",
        TEST_SENT = "Tesztüzenet elküldve a kísérőprogramnak.",
        HELP = "Parancsok: /wct (állapot), /wct on (bekapcsolás), /wct test (tesztüzenet), /wct pos (chat helyzetének igazítása), /wct toggle (megjelenítés/elrejtés)",
        COMPANION_OFF = "A kísérőprogram nem található: a fordítás ki van kapcsolva. Indítsd el a WoWChatTranslatorCompagnion programot, majd írd be: /wct on.",
        BINDING_TOGGLE = "Fordítási réteg megjelenítése / elrejtése",
        BINDING_SCREENSHOT = "Képernyőkép a fordítási réteggel",
        SCREENSHOT_OFF = "Nincs fordítási réteg: képernyőkép nem lehetséges.",
        OVERLAY_HIDDEN = "Fordítási réteg elrejtve (%s vagy /wct toggle a megjelenítéshez).",
        OVERLAY_HIDDEN_NOKEY = "Fordítási réteg elrejtve (/wct toggle a megjelenítéshez).",
        OVERLAY_SHOWN = "Fordítási réteg megjelenítve.",
    },
    tr = {
        RELOAD_PROMPT = "Sohbetin konumu değişti. Çevirinin sohbetle hizalanması için arayüz yeniden yüklensin mi?",
        RELOAD = "Yeniden yükle",
        LATER = "Daha sonra",
        BRIDGE_ON = "Yardımcı programa köprü: |cff00ff00etkin|r (%d mesaj bekliyor)",
        TEST_SENT = "Test mesajı yardımcı programa gönderildi.",
        HELP = "Komutlar: /wct (durum), /wct on (başlat), /wct test (test mesajı), /wct pos (sohbet konumunu hizala), /wct toggle (göster/gizle)",
        COMPANION_OFF = "Yardımcı program bulunamadı: çeviri kapalı. WoWChatTranslatorCompagnion'u başlatın, ardından /wct on yazın.",
        BINDING_TOGGLE = "Çeviri katmanını göster / gizle",
        BINDING_SCREENSHOT = "Çeviri katmanıyla ekran görüntüsü",
        SCREENSHOT_OFF = "Çeviri katmanı yok: ekran görüntüsü alınamıyor.",
        OVERLAY_HIDDEN = "Çeviri katmanı gizlendi (göstermek için %s veya /wct toggle).",
        OVERLAY_HIDDEN_NOKEY = "Çeviri katmanı gizlendi (göstermek için /wct toggle).",
        OVERLAY_SHOWN = "Çeviri katmanı gösteriliyor.",
    },
    el = {
        RELOAD_PROMPT = "Η θέση της συνομιλίας άλλαξε. Επαναφόρτωση της διεπαφής ώστε η μετάφραση να ταιριάζει με τη συνομιλία;",
        RELOAD = "Επαναφόρτωση",
        LATER = "Αργότερα",
        BRIDGE_ON = "Γέφυρα προς τη βοηθητική εφαρμογή: |cff00ff00ενεργή|r (%d μήνυμα(τα) σε αναμονή)",
        TEST_SENT = "Δοκιμαστικό μήνυμα στάλθηκε στη βοηθητική εφαρμογή.",
        HELP = "Εντολές: /wct (κατάσταση), /wct on (ενεργοποίηση), /wct test (δοκιμαστικό μήνυμα), /wct pos (ευθυγράμμιση θέσης συνομιλίας), /wct toggle (εμφάνιση/απόκρυψη)",
        COMPANION_OFF = "Η βοηθητική εφαρμογή δεν εντοπίστηκε: η μετάφραση είναι ανενεργή. Ξεκινήστε το WoWChatTranslatorCompagnion και γράψτε /wct on.",
        BINDING_TOGGLE = "Εμφάνιση / απόκρυψη του επιπέδου μετάφρασης",
        BINDING_SCREENSHOT = "Στιγμιότυπο οθόνης με το επίπεδο μετάφρασης",
        SCREENSHOT_OFF = "Δεν υπάρχει επίπεδο μετάφρασης: αδύνατο στιγμιότυπο.",
        OVERLAY_HIDDEN = "Το επίπεδο μετάφρασης κρύφτηκε (%s ή /wct toggle για εμφάνιση).",
        OVERLAY_HIDDEN_NOKEY = "Το επίπεδο μετάφρασης κρύφτηκε (/wct toggle για εμφάνιση).",
        OVERLAY_SHOWN = "Το επίπεδο μετάφρασης εμφανίζεται.",
    },
    uk = {
        RELOAD_PROMPT = "Положення чату змінилося. Перезавантажити інтерфейс, щоб переклад збігався з чатом?",
        RELOAD = "Перезавантажити",
        LATER = "Пізніше",
        BRIDGE_ON = "Міст до компаньйона: |cff00ff00активний|r (%d повідомлень у черзі)",
        TEST_SENT = "Тестове повідомлення надіслано компаньйону.",
        HELP = "Команди: /wct (стан), /wct on (увімкнути), /wct test (тестове повідомлення), /wct pos (вирівняти положення чату), /wct toggle (показати/приховати)",
        COMPANION_OFF = "Компаньйона не знайдено: переклад вимкнено. Запустіть WoWChatTranslatorCompagnion, потім введіть /wct on.",
        BINDING_TOGGLE = "Показати / приховати шар перекладу",
        BINDING_SCREENSHOT = "Знімок екрана з шаром перекладу",
        SCREENSHOT_OFF = "Немає шару перекладу: знімок неможливий.",
        OVERLAY_HIDDEN = "Шар перекладу приховано (%s або /wct toggle, щоб показати).",
        OVERLAY_HIDDEN_NOKEY = "Шар перекладу приховано (/wct toggle, щоб показати).",
        OVERLAY_SHOWN = "Шар перекладу показано.",
    },
    bg = {
        RELOAD_PROMPT = "Позицията на чата се промени. Да се презареди ли интерфейсът, за да съвпада преводът с чата?",
        RELOAD = "Презареждане",
        LATER = "По-късно",
        BRIDGE_ON = "Мост към помощника: |cff00ff00активен|r (%d съобщения на опашка)",
        TEST_SENT = "Тестово съобщение е изпратено до помощника.",
        HELP = "Команди: /wct (състояние), /wct on (включване), /wct test (тестово съобщение), /wct pos (подравняване на чата), /wct toggle (показване/скриване)",
        COMPANION_OFF = "Помощникът не е открит: преводът е изключен. Стартирайте WoWChatTranslatorCompagnion, след това въведете /wct on.",
        BINDING_TOGGLE = "Показване / скриване на слоя за превод",
        BINDING_SCREENSHOT = "Екранна снимка със слоя за превод",
        SCREENSHOT_OFF = "Няма слой за превод: снимката е невъзможна.",
        OVERLAY_HIDDEN = "Слоят за превод е скрит (%s или /wct toggle, за да го покажете).",
        OVERLAY_HIDDEN_NOKEY = "Слоят за превод е скрит (/wct toggle, за да го покажете).",
        OVERLAY_SHOWN = "Слоят за превод е показан.",
    },
}
L.enGB = L.enUS
L.esMX = L.esES
L.ptPT = L.ptBR

-- The player's reading language set in the companion (written to Companion.lua, loaded after
-- this file), else the game's language. Resolved on use, once every file is loaded.
local COMPANION_LANGS = {
    en = "enUS", fr = "frFR", de = "deDE", es = "esES", it = "itIT", pt = "ptBR", ru = "ruRU",
}
-- The chat font of a game in another language may lack some letters: Greek, the extra
-- Cyrillic letters, and Latin ones like Czech "ř ě ů" or Polish "ł ż" (drawn as boxes).
-- The companion's overlay is drawn by Windows and shows every alphabet; for the addon's own
-- messages in the game's chat, a language is used only if the chat font draws its letters.
local SCRIPT_SAMPLES = {
    el = { "Α", "Γ", "Δ", "Λ", "Ω" }, uk = { "Ї", "Є", "Ґ", "ї", "є" }, bg = { "Ж", "Щ", "Ъ", "Ю", "Я" },
    pl = { "ł", "ż", "ś", "ź", "ę" }, cs = { "ř", "ě", "ů", "č", "ň" }, sk = { "ľ", "ĺ", "ŕ", "ô", "ť" },
    hu = { "ő", "ű", "Ő", "Ű", "ő" }, ro = { "ș", "ț", "ă", "Ș", "Ț" }, tr = { "ğ", "ş", "ı", "İ", "Ğ" },
}
local MISSING = "\238\128\128" -- U+E000 (private use): drawn as the "missing letter" box
local displayable = {}

local function Width(probe, char)
    probe:SetText(char)
    return probe:GetStringWidth() or 0
end

local function CanDisplay(lang)
    local sample = SCRIPT_SAMPLES[lang]
    if not sample then
        return true
    end
    if displayable[lang] == nil then
        local ok, result = pcall(function()
            local probe = UIParent:CreateFontString(nil, "BACKGROUND")
            probe:SetFontObject(ChatFontNormal or GameFontNormal)
            local box = Width(probe, MISSING)
            local missing = 0
            for _, char in ipairs(sample) do
                local width = Width(probe, char)
                -- Not drawn at all, or drawn as the same box as a missing letter.
                if width < 1 or math.abs(width - box) < 0.01 then
                    missing = missing + 1
                end
            end
            probe:SetText("")
            probe:Hide()
            return missing == 0
        end)
        displayable[lang] = ok and result
    end
    return displayable[lang]
end

local function Active()
    local state = _G.WoWChatTranslatorCompanion
    local lang = type(state) == "table" and state.lang
    if lang then
        local tbl = L[COMPANION_LANGS[lang] or lang]
        if tbl and CanDisplay(lang) then
            return tbl
        end
    end
    return L[GetLocale()] or L.enUS
end

ns.L = setmetatable({}, {
    __index = function(_, key)
        return Active()[key] or L.enUS[key] or key
    end,
})
