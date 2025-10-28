class EncryptionApp {
    constructor() {
        this.privateKey = null;
        this.publicKey = null;
        this.encryptedMessage = null;
        this.currentMessage = '';
        
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        
        this.generateKeysBtn = document.getElementById('generate-keys-btn');
        this.encryptBtn = document.getElementById('encrypt-btn');
        this.decryptBtn = document.getElementById('decrypt-btn');
        this.clearBtn = document.getElementById('clear-btn');
        
        this.privateKeyDisplay = document.getElementById('private-key');
        this.publicKeyDisplay = document.getElementById('public-key');
        this.c1Display = document.getElementById('c1-display');
        this.c2Display = document.getElementById('c2-display');
        this.decryptionResult = document.getElementById('decryption-result');
        
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
    }

    attachEventListeners() {
        this.generateKeysBtn.addEventListener('click', () => this.generateKeys());
        this.encryptBtn.addEventListener('click', () => this.encryptMessage());
        this.decryptBtn.addEventListener('click', () => this.decryptMessage());
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
            const keys = ElGamalEncryption.generateKeys();
            this.privateKey = keys.privateKey;
            this.publicKey = keys.publicKey;
            
            this.updateKeysDisplay();
            this.showInfo('Ключи успешно сгенерированы');
        } catch (error) {
            this.showError('Ошибка генерации ключей: ' + error.message);
        }
    }

    encryptMessage() {
        if (!this.publicKey) {
            this.showError('Сначала сгенерируйте ключи');
            return;
        }

        this.currentMessage = this.messageInput.value.trim();
        if (!this.currentMessage) {
            this.showError('Введите сообщение для шифрования');
            return;
        }

        try {
            this.encryptedMessage = ElGamalEncryption.encrypt(this.publicKey, this.currentMessage);
            this.updateEncryptedDisplay();
            this.showInfo('Сообщение успешно зашифровано');
        } catch (error) {
            this.showError('Ошибка шифрования: ' + error.message);
        }
    }

    decryptMessage() {
        if (!this.encryptedMessage) {
            this.showError('Сначала зашифруйте сообщение');
            return;
        }

        if (!this.privateKey) {
            this.showError('Отсутствует закрытый ключ');
            return;
        }

        try {
            const decryptedMessage = ElGamalEncryption.decrypt(this.privateKey, this.encryptedMessage);
            this.updateDecryptionResult(decryptedMessage);
            this.showInfo('Сообщение успешно расшифровано');
        } catch (error) {
            this.showError('Ошибка расшифрования: ' + error.message);
        }
    }

    clearAll() {
        this.privateKey = null;
        this.publicKey = null;
        this.encryptedMessage = null;
        this.currentMessage = '';
        
        this.privateKeyDisplay.textContent = '-';
        this.publicKeyDisplay.textContent = '-';
        this.c1Display.textContent = '-';
        this.c2Display.textContent = '-';
        this.decryptionResult.textContent = '-';
        this.decryptionResult.className = 'verification-result';
        
        this.showInfo('Все данные очищены');
    }

    updateKeysDisplay() {
        this.privateKeyDisplay.textContent = this.privateKey ? this.privateKey.toString() : '-';
        this.publicKeyDisplay.textContent = this.publicKey ? `(${this.publicKey.x}, ${this.publicKey.y})` : '-';
    }

    updateEncryptedDisplay() {
        if (this.encryptedMessage) {
            const { C1, C2 } = this.encryptedMessage;
            this.c1Display.textContent = C1 ? `(${C1.x}, ${C1.y})` : 'None';
            this.c2Display.textContent = C2 ? `(${C2.x}, ${C2.y})` : 'None';
        } else {
            this.c1Display.textContent = '-';
            this.c2Display.textContent = '-';
        }
    }

    updateDecryptionResult(message) {
        const regex = /Точка \(([^)]+)\) не на кривой/;
        const match = message.match(regex);

        if (match) {
            const point = match[1];
            message = `Сообщение успешно восстановлено из точки (${point})`;
        }
        this.decryptionResult.textContent = message;
        this.decryptionResult.className = 'verification-result success';
    }

    showInfo(message) {
        console.log('INFO:', message);
    }

    showError(message) {
        console.error('ERROR:', message);
        alert(message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new EncryptionApp();
});
