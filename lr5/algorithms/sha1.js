class SHA1 {
    
    constructor() {
        this.h = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0];
        this.k = [0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6];
    }
    
    _leftRotate(value, amount) {
        /** Циклический левый сдвиг 32-битного числа */
        return ((value << amount) | (value >>> (32 - amount))) >>> 0;
    }
    
    _f(t, b, c, d) {
        /** Элементарные логические функции */
        if (t >= 0 && t <= 19) {
            return (b & c) | (~b & d);
        } else if (t >= 20 && t <= 39) {
            return b ^ c ^ d;
        } else if (t >= 40 && t <= 59) {
            return (b & c) | (b & d) | (c & d);
        } else if (t >= 60 && t <= 79) {
            return b ^ c ^ d;
        }
        return 0;
    }
    
    _padMessage(message) {
        let msgBytes;
        
        if (typeof message === 'string') {
            const encoder = new TextEncoder();
            msgBytes = encoder.encode(message);
        } else if (message instanceof Uint8Array) {
            msgBytes = message;
        } else {
            throw new Error('Неподдерживаемый тип сообщения');
        }
        
        const msgLen = msgBytes.length * 8;
        
        // Добавляем бит 1
        const padded = new Uint8Array(msgBytes.length + 1);
        padded.set(msgBytes);
        padded[msgBytes.length] = 0x80;
        
        // Вычисляем необходимую длину с дополнением
        const totalLen = Math.ceil((padded.length * 8 + 64) / 512) * 512 / 8;
        const result = new Uint8Array(totalLen);
        result.set(padded);
        
        // Добавляем длину исходного сообщения (64 бита)
        const lenBytes = new ArrayBuffer(8);
        const lenView = new DataView(lenBytes);
        
        if (msgLen > 0xFFFFFFFF) {
            const high = Math.floor(msgLen / 0x100000000);
            const low = msgLen % 0x100000000;
            lenView.setUint32(0, high, false);
            lenView.setUint32(4, low, false);
        } else {
            lenView.setUint32(0, 0, false);
            lenView.setUint32(4, msgLen, false);
        }
        
        result.set(new Uint8Array(lenBytes), totalLen - 8);
        
        return result;
    }
    
    _processBlock(block) {
        // Разбиваем блок на 16 32-битных слов      
        const w = new Array(80);
        
        for (let i = 0; i < 16; i++) {
            w[i] = (block[i * 4] << 24) |
                   (block[i * 4 + 1] << 16) |
                   (block[i * 4 + 2] << 8) |
                   (block[i * 4 + 3]);
            w[i] >>>= 0; // Обеспечиваем беззнаковость
        }
        
        // Расширяем до 80 слов
        for (let i = 16; i < 80; i++) {
            w[i] = this._leftRotate(w[i - 16] ^ w[i - 14] ^ w[i - 8] ^ w[i - 3], 1);
        }
        
        let [a, b, c, d, e] = this.h;
        
        // 80 раундов
        for (let t = 0; t < 80; t++) {
            const temp = (this._leftRotate(a, 5) + this._f(t, b, c, d) + e + w[t] + this.k[Math.floor(t / 20)]) >>> 0;
            e = d;
            d = c;
            c = this._leftRotate(b, 30);
            b = a;
            a = temp;
        }
        
        // Обновляем значения хеша
        this.h[0] = (this.h[0] + a) >>> 0;
        this.h[1] = (this.h[1] + b) >>> 0;
        this.h[2] = (this.h[2] + c) >>> 0;
        this.h[3] = (this.h[3] + d) >>> 0;
        this.h[4] = (this.h[4] + e) >>> 0;
    }
    
    hash(message) {
        /** Вычисление хеш-функции */
        this.h = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0];
        
        // Дополнение сообщения
        const paddedMsg = this._padMessage(message);
        
        // Обработка блоков по 512 бит
        for (let i = 0; i < paddedMsg.length; i += 64) {
            const block = paddedMsg.subarray(i, i + 64);
            this._processBlock(block);
        }
        
        let result = '';
        for (const hVal of this.h) {
            // Конвертируем каждое 32-битное слово в 8 hex символов
            result += hVal.toString(16).padStart(8, '0');
        }
        
        return result;
    }
    
    hashHex(message) {
        const hashValue = this.hash(message);
        return hashValue;
    }
}
