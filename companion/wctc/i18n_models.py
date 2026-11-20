"""Strings of the model choice and download (first launch window, menu), in every reading language."""

MODEL_TEXTS = {
    "fr": {
        "first_run_title": "Modèle de traduction",
        "first_run_text": "Pour traduire le chat, le compagnon a besoin d'un modèle de traduction. Il est téléchargé "
                          "une seule fois depuis GitHub, quand vous le choisissez.\n\n"
                          "• Standard : rapide, convient à tous les PC.\n"
                          "• Qualité : traductions plus justes, pour les PC puissants (16 Go de mémoire, 8 cœurs).\n\n"
                          "Vous pourrez changer plus tard dans les Options (clic sur l'icône du compagnon).",
        "first_run_recommended": "Conseillé pour ce PC : {name}",
        "first_run_standard": "Standard (~{size} Mo)",
        "first_run_quality": "Qualité (~{size} Mo)",
        "first_run_later": "Plus tard",
        "name_standard": "Standard",
        "name_quality": "Qualité",
        "dl_started": "Téléchargement du modèle {name} ({size} Mo) en arrière-plan…",
        "dl_progress": "{done} / {total} Mo",
        "dl_hide": "Masquer (le téléchargement continue)",
        "dl_ready": "Modèle {name} installé : la traduction est active.",
        "dl_failed": "Le modèle {name} n'a pas pu être téléchargé. Réessayez depuis les Options (onglet Traduction).",
        "no_model": "Aucun modèle de traduction installé : choisissez-en un dans les Options (onglet Traduction).",
        "models_folder_locked": "Le dossier du compagnon est protégé en écriture :\n{path}\n\nAutoriser le compagnon à y "
                                "enregistrer le modèle de traduction ? Windows vous demandera de confirmer (droits "
                                "administrateur).\n\nSi vous refusez, le modèle sera enregistré dans votre dossier "
                                "utilisateur (AppData).",
    },
    "en": {
        "first_run_title": "Translation model",
        "first_run_text": "To translate the chat, the companion needs a translation model. It is downloaded once "
                          "from GitHub, when you choose it.\n\n"
                          "• Standard: fast, suits every PC.\n"
                          "• Quality: more accurate translations, for powerful PCs (16 GB of memory, 8 cores).\n\n"
                          "You can change it later in the Options (click the companion icon).",
        "first_run_recommended": "Recommended for this PC: {name}",
        "first_run_standard": "Standard (~{size} MB)",
        "first_run_quality": "Quality (~{size} MB)",
        "first_run_later": "Later",
        "name_standard": "Standard",
        "name_quality": "Quality",
        "dl_started": "Downloading the {name} model ({size} MB) in the background…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Hide (the download goes on)",
        "dl_ready": "{name} model installed: translation is on.",
        "dl_failed": "The {name} model could not be downloaded. Try again from the Options (Translation tab).",
        "no_model": "No translation model installed: choose one in the Options (Translation tab).",
        "models_folder_locked": "The companion's folder is write-protected:\n{path}\n\nAllow the companion to save "
                                "the translation model there? Windows will ask you to confirm (administrator "
                                "rights).\n\nIf you refuse, the model is saved in your user folder (AppData).",
    },
    "de": {
        "first_run_title": "Übersetzungsmodell",
        "first_run_text": "Um den Chat zu übersetzen, braucht der Begleiter ein Übersetzungsmodell. Es wird einmalig "
                          "von GitHub heruntergeladen, wenn du es auswählst.\n\n"
                          "• Standard: schnell, für jeden PC geeignet.\n"
                          "• Qualität: genauere Übersetzungen, für leistungsstarke PCs (16 GB Arbeitsspeicher, 8 Kerne).\n\n"
                          "Du kannst es später im Menü „Übersetzungsmodell“ (Optionen) ändern.",
        "first_run_recommended": "Empfohlen für diesen PC: {name}",
        "first_run_standard": "Standard (~{size} MB)",
        "first_run_quality": "Qualität (~{size} MB)",
        "first_run_later": "Später",
        "name_standard": "Standard",
        "name_quality": "Qualität",
        "dl_started": "Modell {name} ({size} MB) wird im Hintergrund heruntergeladen…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Ausblenden (der Download läuft weiter)",
        "dl_ready": "Modell {name} installiert: die Übersetzung ist aktiv.",
        "dl_failed": "Das Modell {name} konnte nicht heruntergeladen werden. Versuche es erneut über das Menü „Übersetzungsmodell“ (Optionen).",
        "no_model": "Kein Übersetzungsmodell installiert: wähle eines im Menü „Übersetzungsmodell“ (Optionen).",
        "models_folder_locked": "Der Ordner des Begleiters ist schreibgeschützt:\n{path}\n\nDem Begleiter erlauben, das "
                                "Übersetzungsmodell dort zu speichern? Windows fragt nach einer Bestätigung "
                                "(Administratorrechte).\n\nWenn du ablehnst, wird das Modell in deinem Benutzerordner "
                                "(AppData) gespeichert.",
    },
    "es": {
        "first_run_title": "Modelo de traducción",
        "first_run_text": "Para traducir el chat, el compañero necesita un modelo de traducción. Se descarga una sola "
                          "vez desde GitHub, cuando lo eliges.\n\n"
                          "• Estándar: rápido, sirve para cualquier PC.\n"
                          "• Calidad: traducciones más precisas, para PC potentes (16 GB de memoria, 8 núcleos).\n\n"
                          "Podrás cambiarlo más tarde en el menú «Modelo de traducción» (Opciones).",
        "first_run_recommended": "Recomendado para este PC: {name}",
        "first_run_standard": "Estándar (~{size} MB)",
        "first_run_quality": "Calidad (~{size} MB)",
        "first_run_later": "Más tarde",
        "name_standard": "Estándar",
        "name_quality": "Calidad",
        "dl_started": "Descargando el modelo {name} ({size} MB) en segundo plano…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Ocultar (la descarga continúa)",
        "dl_ready": "Modelo {name} instalado: la traducción está activa.",
        "dl_failed": "No se pudo descargar el modelo {name}. Inténtalo de nuevo desde el menú «Modelo de traducción» (Opciones).",
        "no_model": "Ningún modelo de traducción instalado: elige uno en el menú «Modelo de traducción» (Opciones).",
        "models_folder_locked": "La carpeta del compañero está protegida contra escritura:\n{path}\n\n¿Permitir que el "
                                "compañero guarde allí el modelo de traducción? Windows te pedirá confirmación "
                                "(derechos de administrador).\n\nSi lo rechazas, el modelo se guardará en tu carpeta "
                                "de usuario (AppData).",
    },
    "it": {
        "first_run_title": "Modello di traduzione",
        "first_run_text": "Per tradurre la chat, il companion ha bisogno di un modello di traduzione. Viene scaricato "
                          "una sola volta da GitHub, quando lo scegli.\n\n"
                          "• Standard: veloce, adatto a ogni PC.\n"
                          "• Qualità: traduzioni più precise, per PC potenti (16 GB di memoria, 8 core).\n\n"
                          "Potrai cambiarlo in seguito nel menu «Modello di traduzione» (Opzioni).",
        "first_run_recommended": "Consigliato per questo PC: {name}",
        "first_run_standard": "Standard (~{size} MB)",
        "first_run_quality": "Qualità (~{size} MB)",
        "first_run_later": "Più tardi",
        "name_standard": "Standard",
        "name_quality": "Qualità",
        "dl_started": "Download del modello {name} ({size} MB) in background…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Nascondi (il download continua)",
        "dl_ready": "Modello {name} installato: la traduzione è attiva.",
        "dl_failed": "Impossibile scaricare il modello {name}. Riprova dal menu «Modello di traduzione» (Opzioni).",
        "no_model": "Nessun modello di traduzione installato: scegline uno nel menu «Modello di traduzione» (Opzioni).",
        "models_folder_locked": "La cartella del companion è protetta da scrittura:\n{path}\n\nConsentire al companion di "
                                "salvarvi il modello di traduzione? Windows ti chiederà conferma (diritti di "
                                "amministratore).\n\nSe rifiuti, il modello verrà salvato nella tua cartella utente "
                                "(AppData).",
    },
    "pt": {
        "first_run_title": "Modelo de tradução",
        "first_run_text": "Para traduzir o chat, o companheiro precisa de um modelo de tradução. Ele é baixado uma "
                          "única vez do GitHub, quando você o escolhe.\n\n"
                          "• Padrão: rápido, serve para qualquer PC.\n"
                          "• Qualidade: traduções mais precisas, para PCs potentes (16 GB de memória, 8 núcleos).\n\n"
                          "Você poderá mudar depois no menu \"Modelo de tradução\" (Opções).",
        "first_run_recommended": "Recomendado para este PC: {name}",
        "first_run_standard": "Padrão (~{size} MB)",
        "first_run_quality": "Qualidade (~{size} MB)",
        "first_run_later": "Mais tarde",
        "name_standard": "Padrão",
        "name_quality": "Qualidade",
        "dl_started": "Baixando o modelo {name} ({size} MB) em segundo plano…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Ocultar (o download continua)",
        "dl_ready": "Modelo {name} instalado: a tradução está ativa.",
        "dl_failed": "Não foi possível baixar o modelo {name}. Tente de novo pelo menu \"Modelo de tradução\" (Opções).",
        "no_model": "Nenhum modelo de tradução instalado: escolha um no menu \"Modelo de tradução\" (Opções).",
        "models_folder_locked": "A pasta do companheiro está protegida contra gravação:\n{path}\n\nPermitir que o "
                                "companheiro salve o modelo de tradução nela? O Windows pedirá confirmação (direitos "
                                "de administrador).\n\nSe você recusar, o modelo será salvo na sua pasta de usuário "
                                "(AppData).",
    },
    "ru": {
        "first_run_title": "Модель перевода",
        "first_run_text": "Чтобы переводить чат, компаньону нужна модель перевода. Она скачивается один раз с GitHub, "
                          "когда вы её выбираете.\n\n"
                          "• Стандарт: быстрая, подходит для любого ПК.\n"
                          "• Качество: более точный перевод, для мощных ПК (16 ГБ памяти, 8 ядер).\n\n"
                          "Позже её можно сменить в меню «Модель перевода» (Настройки).",
        "first_run_recommended": "Рекомендуется для этого ПК: {name}",
        "first_run_standard": "Стандарт (~{size} МБ)",
        "first_run_quality": "Качество (~{size} МБ)",
        "first_run_later": "Позже",
        "name_standard": "Стандарт",
        "name_quality": "Качество",
        "dl_started": "Модель «{name}» ({size} МБ) скачивается в фоне…",
        "dl_progress": "{done} / {total} МБ",
        "dl_hide": "Скрыть (загрузка продолжится)",
        "dl_ready": "Модель «{name}» установлена: перевод включён.",
        "dl_failed": "Не удалось скачать модель «{name}». Попробуйте снова через меню «Модель перевода» (Настройки).",
        "no_model": "Модель перевода не установлена: выберите её в меню «Модель перевода» (Настройки).",
        "models_folder_locked": "Папка компаньона защищена от записи:\n{path}\n\nРазрешить компаньону сохранить туда "
                                "модель перевода? Windows попросит подтверждение (права администратора).\n\nЕсли вы "
                                "откажетесь, модель будет сохранена в папке пользователя (AppData).",
    },
    "pl": {
        "first_run_title": "Model tłumaczenia",
        "first_run_text": "Aby tłumaczyć czat, towarzysz potrzebuje modelu tłumaczenia. Jest pobierany jeden raz "
                          "z GitHuba, gdy go wybierzesz.\n\n"
                          "• Standard: szybki, pasuje do każdego PC.\n"
                          "• Jakość: dokładniejsze tłumaczenia, dla mocnych PC (16 GB pamięci, 8 rdzeni).\n\n"
                          "Możesz go później zmienić w menu „Model tłumaczenia” (Opcje).",
        "first_run_recommended": "Zalecany dla tego PC: {name}",
        "first_run_standard": "Standard (~{size} MB)",
        "first_run_quality": "Jakość (~{size} MB)",
        "first_run_later": "Później",
        "name_standard": "Standard",
        "name_quality": "Jakość",
        "dl_started": "Pobieranie modelu {name} ({size} MB) w tle…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Ukryj (pobieranie trwa dalej)",
        "dl_ready": "Model {name} zainstalowany: tłumaczenie jest włączone.",
        "dl_failed": "Nie udało się pobrać modelu {name}. Spróbuj ponownie z menu „Model tłumaczenia” (Opcje).",
        "no_model": "Brak zainstalowanego modelu tłumaczenia: wybierz go w menu „Model tłumaczenia” (Opcje).",
        "models_folder_locked": "Folder towarzysza jest chroniony przed zapisem:\n{path}\n\nPozwolić towarzyszowi "
                                "zapisać tam model tłumaczenia? Windows poprosi o potwierdzenie (uprawnienia "
                                "administratora).\n\nJeśli odmówisz, model zostanie zapisany w folderze użytkownika "
                                "(AppData).",
    },
    "nl": {
        "first_run_title": "Vertaalmodel",
        "first_run_text": "Om de chat te vertalen heeft de companion een vertaalmodel nodig. Het wordt één keer van "
                          "GitHub gedownload, wanneer je het kiest.\n\n"
                          "• Standaard: snel, geschikt voor elke pc.\n"
                          "• Kwaliteit: nauwkeurigere vertalingen, voor krachtige pc's (16 GB geheugen, 8 kernen).\n\n"
                          "Je kunt het later wijzigen in het menu ‘Vertaalmodel’ (Opties).",
        "first_run_recommended": "Aanbevolen voor deze pc: {name}",
        "first_run_standard": "Standaard (~{size} MB)",
        "first_run_quality": "Kwaliteit (~{size} MB)",
        "first_run_later": "Later",
        "name_standard": "Standaard",
        "name_quality": "Kwaliteit",
        "dl_started": "Model {name} ({size} MB) wordt op de achtergrond gedownload…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Verbergen (de download gaat door)",
        "dl_ready": "Model {name} geïnstalleerd: vertalen staat aan.",
        "dl_failed": "Model {name} kon niet worden gedownload. Probeer het opnieuw via het menu ‘Vertaalmodel’ (Opties).",
        "no_model": "Geen vertaalmodel geïnstalleerd: kies er een in het menu ‘Vertaalmodel’ (Opties).",
        "models_folder_locked": "De map van de companion is tegen schrijven beveiligd:\n{path}\n\nDe companion toestaan "
                                "het vertaalmodel daar op te slaan? Windows vraagt om bevestiging "
                                "(beheerdersrechten).\n\nAls je weigert, wordt het model in je gebruikersmap "
                                "(AppData) opgeslagen.",
    },
    "sv": {
        "first_run_title": "Översättningsmodell",
        "first_run_text": "För att översätta chatten behöver följeslagaren en översättningsmodell. Den laddas ner en "
                          "gång från GitHub, när du väljer den.\n\n"
                          "• Standard: snabb, passar alla datorer.\n"
                          "• Kvalitet: exaktare översättningar, för kraftfulla datorer (16 GB minne, 8 kärnor).\n\n"
                          "Du kan byta senare i menyn ”Översättningsmodell” (Alternativ).",
        "first_run_recommended": "Rekommenderas för den här datorn: {name}",
        "first_run_standard": "Standard (~{size} MB)",
        "first_run_quality": "Kvalitet (~{size} MB)",
        "first_run_later": "Senare",
        "name_standard": "Standard",
        "name_quality": "Kvalitet",
        "dl_started": "Laddar ner modellen {name} ({size} MB) i bakgrunden…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Dölj (nedladdningen fortsätter)",
        "dl_ready": "Modellen {name} är installerad: översättningen är på.",
        "dl_failed": "Modellen {name} kunde inte laddas ner. Försök igen från menyn ”Översättningsmodell” (Alternativ).",
        "no_model": "Ingen översättningsmodell installerad: välj en i menyn ”Översättningsmodell” (Alternativ).",
        "models_folder_locked": "Följeslagarens mapp är skrivskyddad:\n{path}\n\nTillåta följeslagaren att spara "
                                "översättningsmodellen där? Windows ber dig bekräfta (administratörsrättigheter).\n\n"
                                "Om du vägrar sparas modellen i din användarmapp (AppData).",
    },
    "da": {
        "first_run_title": "Oversættelsesmodel",
        "first_run_text": "For at oversætte chatten skal ledsageren bruge en oversættelsesmodel. Den hentes én gang "
                          "fra GitHub, når du vælger den.\n\n"
                          "• Standard: hurtig, passer til alle pc'er.\n"
                          "• Kvalitet: mere præcise oversættelser, til kraftige pc'er (16 GB hukommelse, 8 kerner).\n\n"
                          "Du kan skifte senere i menuen \"Oversættelsesmodel\" (Indstillinger).",
        "first_run_recommended": "Anbefalet til denne pc: {name}",
        "first_run_standard": "Standard (~{size} MB)",
        "first_run_quality": "Kvalitet (~{size} MB)",
        "first_run_later": "Senere",
        "name_standard": "Standard",
        "name_quality": "Kvalitet",
        "dl_started": "Henter modellen {name} ({size} MB) i baggrunden…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Skjul (overførslen fortsætter)",
        "dl_ready": "Modellen {name} er installeret: oversættelsen er slået til.",
        "dl_failed": "Modellen {name} kunne ikke hentes. Prøv igen fra menuen \"Oversættelsesmodel\" (Indstillinger).",
        "no_model": "Ingen oversættelsesmodel installeret: vælg en i menuen \"Oversættelsesmodel\" (Indstillinger).",
        "models_folder_locked": "Ledsagerens mappe er skrivebeskyttet:\n{path}\n\nTillad ledsageren at gemme "
                                "oversættelsesmodellen der? Windows beder dig bekræfte (administratorrettigheder).\n\n"
                                "Hvis du afviser, gemmes modellen i din brugermappe (AppData).",
    },
    "no": {
        "first_run_title": "Oversettelsesmodell",
        "first_run_text": "For å oversette chatten trenger følgesvennen en oversettelsesmodell. Den lastes ned én "
                          "gang fra GitHub, når du velger den.\n\n"
                          "• Standard: rask, passer for alle PC-er.\n"
                          "• Kvalitet: mer presise oversettelser, for kraftige PC-er (16 GB minne, 8 kjerner).\n\n"
                          "Du kan bytte senere i menyen «Oversettelsesmodell» (Innstillinger).",
        "first_run_recommended": "Anbefalt for denne PC-en: {name}",
        "first_run_standard": "Standard (~{size} MB)",
        "first_run_quality": "Kvalitet (~{size} MB)",
        "first_run_later": "Senere",
        "name_standard": "Standard",
        "name_quality": "Kvalitet",
        "dl_started": "Laster ned modellen {name} ({size} MB) i bakgrunnen…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Skjul (nedlastingen fortsetter)",
        "dl_ready": "Modellen {name} er installert: oversettelsen er på.",
        "dl_failed": "Modellen {name} kunne ikke lastes ned. Prøv igjen fra menyen «Oversettelsesmodell» (Innstillinger).",
        "no_model": "Ingen oversettelsesmodell installert: velg en i menyen «Oversettelsesmodell» (Innstillinger).",
        "models_folder_locked": "Følgesvennens mappe er skrivebeskyttet:\n{path}\n\nTillate følgesvennen å lagre "
                                "oversettelsesmodellen der? Windows ber deg bekrefte (administratorrettigheter).\n\n"
                                "Hvis du nekter, lagres modellen i brukermappen din (AppData).",
    },
    "fi": {
        "first_run_title": "Käännösmalli",
        "first_run_text": "Chatin kääntämiseen seuralainen tarvitsee käännösmallin. Se ladataan kerran GitHubista, "
                          "kun valitset sen.\n\n"
                          "• Vakio: nopea, sopii kaikille tietokoneille.\n"
                          "• Laatu: tarkemmat käännökset, tehokkaille tietokoneille (16 Gt muistia, 8 ydintä).\n\n"
                          "Voit vaihtaa sen myöhemmin valikossa ”Käännösmalli” (Asetukset).",
        "first_run_recommended": "Suositeltu tälle tietokoneelle: {name}",
        "first_run_standard": "Vakio (~{size} Mt)",
        "first_run_quality": "Laatu (~{size} Mt)",
        "first_run_later": "Myöhemmin",
        "name_standard": "Vakio",
        "name_quality": "Laatu",
        "dl_started": "Ladataan mallia {name} ({size} Mt) taustalla…",
        "dl_progress": "{done} / {total} Mt",
        "dl_hide": "Piilota (lataus jatkuu)",
        "dl_ready": "Malli {name} asennettu: kääntäminen on käytössä.",
        "dl_failed": "Mallia {name} ei voitu ladata. Yritä uudelleen valikosta ”Käännösmalli” (Asetukset).",
        "no_model": "Käännösmallia ei ole asennettu: valitse se valikosta ”Käännösmalli” (Asetukset).",
        "models_folder_locked": "Seuralaisen kansio on kirjoitussuojattu:\n{path}\n\nSallitaanko seuralaisen tallentaa "
                                "käännösmalli sinne? Windows pyytää vahvistusta (järjestelmänvalvojan "
                                "oikeudet).\n\nJos kieltäydyt, malli tallennetaan käyttäjäkansioosi (AppData).",
    },
    "cs": {
        "first_run_title": "Model překladu",
        "first_run_text": "K překládání chatu potřebuje společník překladový model. Stáhne se jednou z GitHubu, "
                          "když si ho vyberete.\n\n"
                          "• Standardní: rychlý, hodí se pro každé PC.\n"
                          "• Kvalitní: přesnější překlady, pro výkonná PC (16 GB paměti, 8 jader).\n\n"
                          "Později ho můžete změnit v nabídce „Model překladu“ (Možnosti).",
        "first_run_recommended": "Doporučeno pro toto PC: {name}",
        "first_run_standard": "Standardní (~{size} MB)",
        "first_run_quality": "Kvalitní (~{size} MB)",
        "first_run_later": "Později",
        "name_standard": "Standardní",
        "name_quality": "Kvalitní",
        "dl_started": "Model {name} ({size} MB) se stahuje na pozadí…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Skrýt (stahování pokračuje)",
        "dl_ready": "Model {name} je nainstalován: překlad je zapnutý.",
        "dl_failed": "Model {name} se nepodařilo stáhnout. Zkuste to znovu z nabídky „Model překladu“ (Možnosti).",
        "no_model": "Není nainstalován žádný překladový model: vyberte ho v nabídce „Model překladu“ (Možnosti).",
        "models_folder_locked": "Složka společníka je chráněna proti zápisu:\n{path}\n\nPovolit společníkovi uložit tam "
                                "překladový model? Windows vás požádá o potvrzení (práva správce).\n\nPokud odmítnete, "
                                "model se uloží do vaší uživatelské složky (AppData).",
    },
    "sk": {
        "first_run_title": "Model prekladu",
        "first_run_text": "Na preklad chatu potrebuje spoločník prekladový model. Stiahne sa raz z GitHubu, keď si "
                          "ho vyberiete.\n\n"
                          "• Štandardný: rýchly, hodí sa pre každé PC.\n"
                          "• Kvalitný: presnejšie preklady, pre výkonné PC (16 GB pamäte, 8 jadier).\n\n"
                          "Neskôr ho môžete zmeniť v ponuke „Model prekladu“ (Možnosti).",
        "first_run_recommended": "Odporúčané pre toto PC: {name}",
        "first_run_standard": "Štandardný (~{size} MB)",
        "first_run_quality": "Kvalitný (~{size} MB)",
        "first_run_later": "Neskôr",
        "name_standard": "Štandardný",
        "name_quality": "Kvalitný",
        "dl_started": "Model {name} ({size} MB) sa sťahuje na pozadí…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Skryť (sťahovanie pokračuje)",
        "dl_ready": "Model {name} je nainštalovaný: preklad je zapnutý.",
        "dl_failed": "Model {name} sa nepodarilo stiahnuť. Skúste to znova z ponuky „Model prekladu“ (Možnosti).",
        "no_model": "Nie je nainštalovaný žiadny prekladový model: vyberte ho v ponuke „Model prekladu“ (Možnosti).",
        "models_folder_locked": "Priečinok spoločníka je chránený proti zápisu:\n{path}\n\nPovoliť spoločníkovi uložiť "
                                "tam prekladový model? Windows vás požiada o potvrdenie (práva správcu).\n\nAk "
                                "odmietnete, model sa uloží do vášho používateľského priečinka (AppData).",
    },
    "ro": {
        "first_run_title": "Model de traducere",
        "first_run_text": "Pentru a traduce chatul, companionul are nevoie de un model de traducere. Este descărcat o "
                          "singură dată de pe GitHub, când îl alegi.\n\n"
                          "• Standard: rapid, potrivit pentru orice PC.\n"
                          "• Calitate: traduceri mai exacte, pentru PC-uri puternice (16 GB memorie, 8 nuclee).\n\n"
                          "Îl poți schimba mai târziu din meniul „Model de traducere” (Opțiuni).",
        "first_run_recommended": "Recomandat pentru acest PC: {name}",
        "first_run_standard": "Standard (~{size} MB)",
        "first_run_quality": "Calitate (~{size} MB)",
        "first_run_later": "Mai târziu",
        "name_standard": "Standard",
        "name_quality": "Calitate",
        "dl_started": "Se descarcă modelul {name} ({size} MB) în fundal…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Ascunde (descărcarea continuă)",
        "dl_ready": "Modelul {name} este instalat: traducerea este activă.",
        "dl_failed": "Modelul {name} nu a putut fi descărcat. Încearcă din nou din meniul „Model de traducere” (Opțiuni).",
        "no_model": "Niciun model de traducere instalat: alege unul din meniul „Model de traducere” (Opțiuni).",
        "models_folder_locked": "Dosarul companionului este protejat la scriere:\n{path}\n\nPermiți companionului să "
                                "salveze acolo modelul de traducere? Windows îți va cere confirmarea (drepturi de "
                                "administrator).\n\nDacă refuzi, modelul va fi salvat în dosarul tău de utilizator "
                                "(AppData).",
    },
    "hu": {
        "first_run_title": "Fordítási modell",
        "first_run_text": "A chat fordításához a társprogramnak fordítási modellre van szüksége. Egyszer töltődik le a "
                          "GitHubról, amikor kiválasztod.\n\n"
                          "• Normál: gyors, minden géphez jó.\n"
                          "• Minőségi: pontosabb fordítás, erős gépekhez (16 GB memória, 8 mag).\n\n"
                          "Később a „Fordítási modell” (Beállítások) menüben módosíthatod.",
        "first_run_recommended": "Ajánlott ehhez a géphez: {name}",
        "first_run_standard": "Normál (~{size} MB)",
        "first_run_quality": "Minőségi (~{size} MB)",
        "first_run_later": "Később",
        "name_standard": "Normál",
        "name_quality": "Minőségi",
        "dl_started": "A(z) {name} modell ({size} MB) letöltése a háttérben…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Elrejtés (a letöltés folytatódik)",
        "dl_ready": "A(z) {name} modell telepítve: a fordítás be van kapcsolva.",
        "dl_failed": "A(z) {name} modellt nem sikerült letölteni. Próbáld újra a „Fordítási modell” (Beállítások) menüből.",
        "no_model": "Nincs telepített fordítási modell: válassz egyet a „Fordítási modell” (Beállítások) menüben.",
        "models_folder_locked": "A társprogram mappája írásvédett:\n{path}\n\nEngedélyezed, hogy a társprogram oda mentse "
                                "a fordítási modellt? A Windows megerősítést kér (rendszergazdai jog).\n\nHa elutasítod, "
                                "a modell a felhasználói mappádba (AppData) kerül.",
    },
    "tr": {
        "first_run_title": "Çeviri modeli",
        "first_run_text": "Sohbeti çevirmek için yardımcı programın bir çeviri modeline ihtiyacı var. Seçtiğinizde "
                          "GitHub'dan bir kez indirilir.\n\n"
                          "• Standart: hızlı, her bilgisayara uygun.\n"
                          "• Kalite: daha doğru çeviriler, güçlü bilgisayarlar için (16 GB bellek, 8 çekirdek).\n\n"
                          "Daha sonra \"Çeviri modeli\" (Seçenekler) menüsünden değiştirebilirsiniz.",
        "first_run_recommended": "Bu bilgisayar için önerilen: {name}",
        "first_run_standard": "Standart (~{size} MB)",
        "first_run_quality": "Kalite (~{size} MB)",
        "first_run_later": "Daha sonra",
        "name_standard": "Standart",
        "name_quality": "Kalite",
        "dl_started": "{name} modeli ({size} MB) arka planda indiriliyor…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Gizle (indirme devam eder)",
        "dl_ready": "{name} modeli kuruldu: çeviri açık.",
        "dl_failed": "{name} modeli indirilemedi. \"Çeviri modeli\" (Seçenekler) menüsünden tekrar deneyin.",
        "no_model": "Kurulu çeviri modeli yok: \"Çeviri modeli\" (Seçenekler) menüsünden birini seçin.",
        "models_folder_locked": "Yardımcı programın klasörü yazmaya karşı korumalı:\n{path}\n\nYardımcı programın çeviri "
                                "modelini oraya kaydetmesine izin verilsin mi? Windows onay isteyecek (yönetici "
                                "hakları).\n\nReddederseniz model kullanıcı klasörünüze (AppData) kaydedilir.",
    },
    "el": {
        "first_run_title": "Μοντέλο μετάφρασης",
        "first_run_text": "Για να μεταφράζει τη συνομιλία, ο σύντροφος χρειάζεται ένα μοντέλο μετάφρασης. Κατεβαίνει "
                          "μία φορά από το GitHub, όταν το επιλέξετε.\n\n"
                          "• Βασικό: γρήγορο, για κάθε υπολογιστή.\n"
                          "• Ποιότητα: πιο ακριβείς μεταφράσεις, για ισχυρούς υπολογιστές (16 GB μνήμη, 8 πυρήνες).\n\n"
                          "Μπορείτε να το αλλάξετε αργότερα από το μενού «Μοντέλο μετάφρασης» (Επιλογές).",
        "first_run_recommended": "Προτείνεται για αυτόν τον υπολογιστή: {name}",
        "first_run_standard": "Βασικό (~{size} MB)",
        "first_run_quality": "Ποιότητα (~{size} MB)",
        "first_run_later": "Αργότερα",
        "name_standard": "Βασικό",
        "name_quality": "Ποιότητα",
        "dl_started": "Λήψη του μοντέλου {name} ({size} MB) στο παρασκήνιο…",
        "dl_progress": "{done} / {total} MB",
        "dl_hide": "Απόκρυψη (η λήψη συνεχίζεται)",
        "dl_ready": "Το μοντέλο {name} εγκαταστάθηκε: η μετάφραση είναι ενεργή.",
        "dl_failed": "Δεν ήταν δυνατή η λήψη του μοντέλου {name}. Δοκιμάστε ξανά από το μενού «Μοντέλο μετάφρασης» (Επιλογές).",
        "no_model": "Δεν έχει εγκατασταθεί μοντέλο μετάφρασης: επιλέξτε ένα από το μενού «Μοντέλο μετάφρασης» (Επιλογές).",
        "models_folder_locked": "Ο φάκελος του συντρόφου προστατεύεται από εγγραφή:\n{path}\n\nΝα επιτραπεί στον σύντροφο "
                                "να αποθηκεύσει εκεί το μοντέλο μετάφρασης; Τα Windows θα ζητήσουν επιβεβαίωση "
                                "(δικαιώματα διαχειριστή).\n\nΑν αρνηθείτε, το μοντέλο θα αποθηκευτεί στον φάκελο "
                                "χρήστη σας (AppData).",
    },
    "uk": {
        "first_run_title": "Модель перекладу",
        "first_run_text": "Щоб перекладати чат, компаньйону потрібна модель перекладу. Вона завантажується один раз "
                          "із GitHub, коли ви її обираєте.\n\n"
                          "• Стандарт: швидка, підходить для будь-якого ПК.\n"
                          "• Якість: точніший переклад, для потужних ПК (16 ГБ пам'яті, 8 ядер).\n\n"
                          "Пізніше її можна змінити в меню «Модель перекладу» (Налаштування).",
        "first_run_recommended": "Рекомендовано для цього ПК: {name}",
        "first_run_standard": "Стандарт (~{size} МБ)",
        "first_run_quality": "Якість (~{size} МБ)",
        "first_run_later": "Пізніше",
        "name_standard": "Стандарт",
        "name_quality": "Якість",
        "dl_started": "Модель «{name}» ({size} МБ) завантажується у фоні…",
        "dl_progress": "{done} / {total} МБ",
        "dl_hide": "Сховати (завантаження триває)",
        "dl_ready": "Модель «{name}» встановлено: переклад увімкнено.",
        "dl_failed": "Не вдалося завантажити модель «{name}». Спробуйте ще раз через меню «Модель перекладу» (Налаштування).",
        "no_model": "Модель перекладу не встановлено: оберіть її в меню «Модель перекладу» (Налаштування).",
        "models_folder_locked": "Папка компаньйона захищена від запису:\n{path}\n\nДозволити компаньйону зберегти туди "
                                "модель перекладу? Windows попросить підтвердження (права адміністратора).\n\nЯкщо ви "
                                "відмовитеся, модель буде збережено в папці користувача (AppData).",
    },
    "bg": {
        "first_run_title": "Модел за превод",
        "first_run_text": "За да превежда чата, придружителят се нуждае от модел за превод. Той се изтегля веднъж от "
                          "GitHub, когато го изберете.\n\n"
                          "• Стандартен: бърз, подходящ за всеки компютър.\n"
                          "• Качествен: по-точни преводи, за мощни компютри (16 GB памет, 8 ядра).\n\n"
                          "По-късно можете да го смените от менюто „Модел за превод“ (Настройки).",
        "first_run_recommended": "Препоръчан за този компютър: {name}",
        "first_run_standard": "Стандартен (~{size} MB)",
        "first_run_quality": "Качествен (~{size} MB)",
        "first_run_later": "По-късно",
        "name_standard": "Стандартен",
        "name_quality": "Качествен",
        "dl_started": "Моделът „{name}“ ({size} MB) се изтегля във фонов режим…",
        "dl_progress": "{done} / {total} МБ",
        "dl_hide": "Скрий (изтеглянето продължава)",
        "dl_ready": "Моделът „{name}“ е инсталиран: преводът е включен.",
        "dl_failed": "Моделът „{name}“ не можа да бъде изтеглен. Опитайте отново от менюто „Модел за превод“ (Настройки).",
        "no_model": "Няма инсталиран модел за превод: изберете от менюто „Модел за превод“ (Настройки).",
        "models_folder_locked": "Папката на придружителя е защитена от запис:\n{path}\n\nДа се разреши ли на "
                                "придружителя да запише там модела за превод? Windows ще поиска потвърждение (права "
                                "на администратор).\n\nАко откажете, моделът ще бъде записан в потребителската ви "
                                "папка (AppData).",
    },
}

# Options window (the tray menu only keeps what is used while playing).
OPTION_TEXTS = {
    "fr": ("Options…", "Options", "Traduction", "Affichage", "Général", "Automatique (langue du jeu)", "Fermer",
           "Version {version}", "installé", "Téléchargement du modèle {name} : {percent} %"),
    "en": ("Options…", "Options", "Translation", "Display", "General", "Automatic (game language)", "Close",
           "Version {version}", "installed", "Downloading the {name} model: {percent} %"),
    "de": ("Optionen…", "Optionen", "Übersetzung", "Anzeige", "Allgemein", "Automatisch (Spielsprache)", "Schließen",
           "Version {version}", "installiert", "Modell {name} wird heruntergeladen: {percent} %"),
    "es": ("Opciones…", "Opciones", "Traducción", "Visualización", "General", "Automático (idioma del juego)", "Cerrar",
           "Versión {version}", "instalado", "Descargando el modelo {name}: {percent} %"),
    "it": ("Opzioni…", "Opzioni", "Traduzione", "Visualizzazione", "Generale", "Automatica (lingua del gioco)", "Chiudi",
           "Versione {version}", "installato", "Download del modello {name}: {percent} %"),
    "pt": ("Opções…", "Opções", "Tradução", "Exibição", "Geral", "Automático (idioma do jogo)", "Fechar",
           "Versão {version}", "instalado", "Baixando o modelo {name}: {percent} %"),
    "ru": ("Настройки…", "Настройки", "Перевод", "Отображение", "Общие", "Автоматически (язык игры)", "Закрыть",
           "Версия {version}", "установлена", "Загрузка модели «{name}»: {percent} %"),
    "pl": ("Opcje…", "Opcje", "Tłumaczenie", "Wygląd", "Ogólne", "Automatycznie (język gry)", "Zamknij",
           "Wersja {version}", "zainstalowany", "Pobieranie modelu {name}: {percent} %"),
    "nl": ("Opties…", "Opties", "Vertaling", "Weergave", "Algemeen", "Automatisch (taal van het spel)", "Sluiten",
           "Versie {version}", "geïnstalleerd", "Model {name} wordt gedownload: {percent} %"),
    "sv": ("Alternativ…", "Alternativ", "Översättning", "Visning", "Allmänt", "Automatiskt (spelets språk)", "Stäng",
           "Version {version}", "installerad", "Laddar ner modellen {name}: {percent} %"),
    "da": ("Indstillinger…", "Indstillinger", "Oversættelse", "Visning", "Generelt", "Automatisk (spillets sprog)",
           "Luk", "Version {version}", "installeret", "Henter modellen {name}: {percent} %"),
    "no": ("Innstillinger…", "Innstillinger", "Oversettelse", "Visning", "Generelt", "Automatisk (spillets språk)",
           "Lukk", "Versjon {version}", "installert", "Laster ned modellen {name}: {percent} %"),
    "fi": ("Asetukset…", "Asetukset", "Käännös", "Näyttö", "Yleiset", "Automaattinen (pelin kieli)", "Sulje",
           "Versio {version}", "asennettu", "Ladataan mallia {name}: {percent} %"),
    "cs": ("Možnosti…", "Možnosti", "Překlad", "Zobrazení", "Obecné", "Automaticky (jazyk hry)", "Zavřít",
           "Verze {version}", "nainstalováno", "Stahování modelu {name}: {percent} %"),
    "sk": ("Možnosti…", "Možnosti", "Preklad", "Zobrazenie", "Všeobecné", "Automaticky (jazyk hry)", "Zavrieť",
           "Verzia {version}", "nainštalované", "Sťahovanie modelu {name}: {percent} %"),
    "ro": ("Opțiuni…", "Opțiuni", "Traducere", "Afișare", "General", "Automat (limba jocului)", "Închide",
           "Versiunea {version}", "instalat", "Se descarcă modelul {name}: {percent} %"),
    "hu": ("Beállítások…", "Beállítások", "Fordítás", "Megjelenés", "Általános", "Automatikus (a játék nyelve)",
           "Bezárás", "Verzió: {version}", "telepítve", "A(z) {name} modell letöltése: {percent} %"),
    "tr": ("Seçenekler…", "Seçenekler", "Çeviri", "Görünüm", "Genel", "Otomatik (oyun dili)", "Kapat",
           "Sürüm {version}", "kurulu", "{name} modeli indiriliyor: %{percent}"),
    "el": ("Επιλογές…", "Επιλογές", "Μετάφραση", "Εμφάνιση", "Γενικά", "Αυτόματα (γλώσσα του παιχνιδιού)", "Κλείσιμο",
           "Έκδοση {version}", "εγκατεστημένο", "Λήψη του μοντέλου {name}: {percent} %"),
    "uk": ("Налаштування…", "Налаштування", "Переклад", "Вигляд", "Загальні", "Автоматично (мова гри)", "Закрити",
           "Версія {version}", "встановлено", "Завантаження моделі «{name}»: {percent} %"),
    "bg": ("Настройки…", "Настройки", "Превод", "Изглед", "Общи", "Автоматично (езикът на играта)", "Затвори",
           "Версия {version}", "инсталиран", "Изтегляне на модела „{name}“: {percent} %"),
}
_OPTION_KEYS = ("menu_options", "opt_title", "tab_translation", "tab_display", "tab_general", "lang_auto",
                "opt_close", "opt_version", "opt_installed", "opt_downloading")
for _lang, _values in OPTION_TEXTS.items():
    MODEL_TEXTS[_lang].update(zip(_OPTION_KEYS, _values))
