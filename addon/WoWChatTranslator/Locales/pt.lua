local _, ns = ...

-- Addon messages (ptBR). English (en.lua) is the fallback for any missing line.
ns.Locales = ns.Locales or {}
ns.Locales.ptBR = {
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
}
