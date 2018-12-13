# Install
```bash
sudo apt-get install portaudio19-dev libffi-dev libssl-dev libmpg123-dev
python -m pip install --upgrade google-assistant-library
python -m pip install --upgrade google-assistant-sdk[samples]
python -m pip install --upgrade google-auth-oauthlib[tool]
```
# Autenticar
```bash
google-oauthlib-tool --scope https://www.googleapis.com/auth/assistant-sdk-prototype \
                        --scope https://www.googleapis.com/auth/gcm \
                        --save --headless --client-secrets /path/to/client_secret_client-id.json
```
