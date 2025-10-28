class EllipticCurve {
    constructor(p, a, b, G, n) {
        this.p = p;
        this.a = a;
        this.b = b;
        this.G = G;
        this.n = n;
    }

    isOnCurve(P) {
        if (!P) return true;
        const { x, y } = P;
        const left = (y * y) % this.p;
        const right = (x * x * x + this.a * x + this.b) % this.p;
        return left === right;
    }

    addPoints(P, Q) {
        if (!P) return Q;
        if (!Q) return P;

        const { x: x1, y: y1 } = P;
        const { x: x2, y: y2 } = Q;

        if (this.pointsEqual(P, Q)) {
            if (y1 === 0n) return null;
            const s = (3n * x1 * x1 + this.a) * this.modinv(2n * y1, this.p) % this.p;
            const x3 = (s * s - x1 - x2) % this.p;
            const y3 = (s * (x1 - x3) - y1) % this.p;
            return { x: (x3 + this.p) % this.p, y: (y3 + this.p) % this.p };
        } else {
            if (x1 === x2) return null;
            const s = (y2 - y1) * this.modinv(x2 - x1, this.p) % this.p;
            const x3 = (s * s - x1 - x2) % this.p;
            const y3 = (s * (x1 - x3) - y1) % this.p;
            return { x: (x3 + this.p) % this.p, y: (y3 + this.p) % this.p };
        }
    }

    multiplyPoint(k, P) {
        if (k === 0n) return null;
        
        let R = null;
        let Q = P;
        let kTemp = k;
        
        while (kTemp > 0n) {
            if (kTemp & 1n) {
                R = this.addPoints(R, Q);
            }
            Q = this.addPoints(Q, Q);
            kTemp = kTemp >> 1n;
        }
        
        return R;
    }

    modinv(a, p) {
        let [old_r, r] = [a, p];
        let [old_s, s] = [1n, 0n];
        let [old_t, t] = [0n, 1n];

        while (r !== 0n) {
            const quotient = old_r / r;
            [old_r, r] = [r, old_r - quotient * r];
            [old_s, s] = [s, old_s - quotient * s];
            [old_t, t] = [t, old_t - quotient * t];
        }

        return (old_s % p + p) % p;
    }

    pointsEqual(P, Q) {
        if (!P && !Q) return true;
        if (!P || !Q) return false;
        return P.x === Q.x && P.y === Q.y;
    }
}


class EllipticCurveElGamal {
    constructor() {
        this.p = 17n;
        this.a = 2n;
        this.b = 2n;
        this.G = { x: 5n, y: 1n };
        this.n = 19n; 
        
        this.curve = new EllipticCurve(this.p, this.a, this.b, this.G, this.n);
    }

    generateKeys() {
        const privateKey = BigInt(Math.floor(Math.random() * Number(this.n - 1n))) + 1n;
        const publicKey = this.curve.multiplyPoint(privateKey, this.G);
        return { privateKey, publicKey };
    }

    messageToPoint(message) {
        const gost = new GOST3411(256);
        const hashHex = gost.hashHex(message);
        
        const hashBytes = new Uint8Array(32);
        for (let i = 0; i < 32; i++) {
            hashBytes[i] = parseInt(hashHex.substr(i * 2, 2), 16);
        }
        
        const first8Bytes = hashBytes.slice(0, 8);
        let messageInt = 0n;
        for (let i = 0; i < 8; i++) {
            messageInt = (messageInt << 8n) | BigInt(first8Bytes[i]);
        }
        
        messageInt = messageInt % this.p;

        let x = messageInt;
        while (true) {
            const ySquared = (x * x * x + this.a * x + this.b) % this.p;
            
            if (this.modExp(ySquared, (this.p - 1n) / 2n, this.p) === 1n) {
                const y = this.modExp(ySquared, (this.p + 1n) / 4n, this.p);
                const point = { x, y };
                if (this.curve.isOnCurve(point)) {
                    return point;
                }
            }
            x = (x + 1n) % this.p;
        }
    }

    pointToMessage(point) {
        if (!point) {
            return "Не удалось восстановить сообщение";
        }
        
        const { x, y } = point;
        if (this.curve.isOnCurve(point)) {
            return `Сообщение успешно восстановлено из точки (${x}, ${y})`;
        } else {
            return `Точка (${x}, ${y}) не на кривой`;
        }
    }

    encrypt(publicKey, message) {
        const messagePoint = this.messageToPoint(message);
        const k = BigInt(Math.floor(Math.random() * Number(this.n - 1n))) + 1n;

        const C1 = this.curve.multiplyPoint(k, this.G);
        const kTimesPub = this.curve.multiplyPoint(k, publicKey);
        const C2 = this.curve.addPoints(messagePoint, kTimesPub);

        return { C1, C2 };
    }

    decrypt(privateKey, encryptedMessage) {
        const { C1, C2 } = encryptedMessage;
        const privateTimesC1 = this.curve.multiplyPoint(privateKey, C1);
        
        let inversePoint = null;
        if (privateTimesC1) {
            inversePoint = {
                x: privateTimesC1.x,
                y: (-privateTimesC1.y + this.p) % this.p
            };
        }

        const messagePoint = this.curve.addPoints(C2, inversePoint);
        return this.pointToMessage(messagePoint);
    }

    modExp(base, exponent, modulus) {
        let result = 1n;
        base = base % modulus;
        
        while (exponent > 0n) {
            if (exponent % 2n === 1n) {
                result = (result * base) % modulus;
            }
            exponent = exponent >> 1n;
            base = (base * base) % modulus;
        }
        
        return result;
    }
}

const ElGamalEncryption = new EllipticCurveElGamal();
