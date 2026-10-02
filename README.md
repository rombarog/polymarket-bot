# Polymarket Alertas

Bot que monitorea los precios de Polymarket y avisa por Telegram cuando un mercado se mueve.

## Qué hace

1. Lee los mercados activos de la API pública de Polymarket.
2. Compara los precios con los de la corrida anterior (`precios.json`).
3. Si un mercado cambia 2 puntos o más, manda un mensaje a Telegram.
4. Guarda los precios nuevos en el repositorio.

Corre solo cada hora con GitHub Actions. No opera con dinero: solo lee datos y avisa.

## Tecnologías

- Python 3 y `requests`
- API pública de Polymarket (Gamma API)
- Telegram Bot API
- GitHub Actions (cron)

## Configuración

1. Creá un bot con @BotFather en Telegram y copiá el token.
2. Averiguá tu chat id escribiéndole al bot y abriendo `https://api.telegram.org/bot<TOKEN>/getUpdates`.
3. En el repo,