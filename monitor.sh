#!/bin/bash

# Esperar a que HAProxy inicie
sleep 15

API_PRINCIPAL="https://techstore-api-1-5grr.onrender.com/"
API_RESPALDO="https://proyectoad2.onrender.com/"

PRINCIPAL_UP=true
RESPALDO_UP=true

send_sms() {
    local msg="$1"
    if [ -z "$TWILIO_SID" ] || [ -z "$TWILIO_TOKEN" ] || [ -z "$TWILIO_PHONE" ] || [ -z "$DESTINATION_PHONE" ]; then
        echo "Faltan credenciales de Twilio. No se envia SMS."
        return
    fi
    curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/Messages.json" \
    --data-urlencode "Body=$msg" \
    --data-urlencode "From=whatsapp:$TWILIO_PHONE" \
    --data-urlencode "To=whatsapp:$DESTINATION_PHONE" \
    -u "$TWILIO_SID:$TWILIO_TOKEN" > /dev/null 2>&1
    echo "SMS Enviado: $msg"
}

while true; do
    # Check principal
    if curl -s "$API_PRINCIPAL" | grep -q "success"; then
        if [ "$PRINCIPAL_UP" = false ]; then
            PRINCIPAL_UP=true
            send_sms "✅ INFO: La API Principal se ha levantado y esta operativa. HAProxy vuelve a usarla."
        fi
    else
        if [ "$PRINCIPAL_UP" = true ]; then
            PRINCIPAL_UP=false
            send_sms "⚠️ ALERTA: La API Principal se ha caido. El balanceador usara el respaldo."
        fi
    fi

    # Check respaldo
    if curl -s "$API_RESPALDO" | grep -q "success"; then
        if [ "$RESPALDO_UP" = false ]; then
            RESPALDO_UP=true
            send_sms "✅ INFO: La API de Respaldo se ha levantado."
        fi
    else
        if [ "$RESPALDO_UP" = true ]; then
            RESPALDO_UP=false
            send_sms "⚠️ ALERTA: La API de Respaldo se ha caido."
        fi
    fi

    sleep 45
done
