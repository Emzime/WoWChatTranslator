local _, ns = ...

-- Addon messages (el). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.el = {
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
}
