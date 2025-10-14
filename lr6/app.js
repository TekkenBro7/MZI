class SignatureApp {
    constructor() {
        this.privateKey = null;
        this.publicKey = null;
        this.signature = null;
        this.currentMessage = '';
        
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        
        this.generateKeysBtn = document.getElementById('generate-keys-btn');
        this.signBtn = document.getElementById('sign-btn');
        this.verifyBtn = document.getElementById('verify-btn');
        this.clearBtn = document.getElementById('clear-btn');
        
        this.privateKeyDisplay = document.getElementById('private-key');
        this.publicKeyDisplay = document.getElementById('public-key');
        this.signatureDisplay = document.getElementById('signature-display');
        this.verificationResult = document.getElementById('verification-result');
        
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
    }

    attachEventListeners() {
        this.generateKeysBtn.addEventListener('click', () => this.generateKeys());
        this.signBtn.addEventListener('click', () => this.signMessage());
        this.verifyBtn.addEventListener('click', () => this.verifySignature());
        this.clearBtn.addEventListener('click', () => this.clearAll());
        
        this.tabButtons.forEach(button => {
            button.addEventListener('click', () => this.switchTab(button));
        });
    }

    switchTab(clickedButton) {
        const tabId = clickedButton.getAttribute('data-tab');
        
        this.tabButtons.forEach(button => button.classList.remove('active'));
        clickedButton.classList.add('active');
        
        this.tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
    }

    generateKeys() {
        try {
            const keys = GOSTSignature.generateKeys();
            this.privateKey = keys.privateKey;
            this.publicKey = keys.publicKey;
            
            this.updateKeysDisplay();
            this.showInfo('Ключи успешно сгенерированы');
        } catch (error) {
            this.showError('Ошибка генерации ключей: ' + error.message);
        }
    }

    signMessage() {
        if (!this.privateKey) {
            this.showError('Сначала сгенерируйте ключи');
            return;
        }

        this.currentMessage = this.messageInput.value.trim();
        if (!this.currentMessage) {
            this.showError('Введите сообщение для подписи');
            return;
        }

        try {
            this.signature = GOSTSignature.signMessage(this.privateKey, this.currentMessage);
            this.updateSignatureDisplay();
            this.showInfo('Сообщение успешно подписано');
        } catch (error) {
            this.showError('Ошибка подписи: ' + error.message);
        }
    }

    verifySignature() {
        if (!this.signature) {
            this.showError('Сначала подпишите сообщение');
            return;
        }

        if (!this.publicKey) {
            this.showError('Отсутствует открытый ключ');
            return;
        }

        const currentMessage = this.messageInput.value.trim();
        if (!currentMessage) {
            this.showError('Введите сообщение для проверки');
            return;
        }

        try {
            const isValid = GOSTSignature.verifySignature(this.publicKey, currentMessage, this.signature);
            this.updateVerificationResult(isValid);
            
            if (isValid) {
                this.showInfo('Подпись верна');
            } else {
                this.showError('Подпись недействительна');
            }
        } catch (error) {
            this.showError('Ошибка проверки: ' + error.message);
        }
    }

    clearAll() {
        this.privateKey = null;
        this.publicKey = null;
        this.signature = null;
        this.currentMessage = '';
        
        this.privateKeyDisplay.textContent = '-';
        this.publicKeyDisplay.textContent = '-';
        this.signatureDisplay.textContent = '-';
        this.verificationResult.textContent = '-';
        this.verificationResult.className = 'verification-result';
        
        this.showInfo('Все данные очищены');
    }

    updateKeysDisplay() {
        this.privateKeyDisplay.textContent = this.privateKey;
        this.publicKeyDisplay.textContent = this.publicKey ? `(${this.publicKey[0]}, ${this.publicKey[1]})` : '-';
    }

    updateSignatureDisplay() {
        if (this.signature) {
            this.signatureDisplay.textContent = `(${this.signature.r}, ${this.signature.s})`;
        } else {
            this.signatureDisplay.textContent = '-';
        }
    }

    updateVerificationResult(isValid) {
        this.verificationResult.textContent = isValid ? '✅ Успешна' : '❌ Ошибка';
        this.verificationResult.className = `verification-result ${isValid ? 'success' : 'error'}`;
    }

    showInfo(message) {
        console.log('INFO:', message);
    }

    showError(message) {
        console.error('ERROR:', message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SignatureApp();
});
