// === Модульная инверсия ===
function modinv(a, p) {
    return modPow(a, p - 2, p);
}

// === Модульное возведение в степень ===
function modPow(base, exponent, modulus) {
    if (modulus === 1) return 0;
    let result = 1;
    base = base % modulus;
    while (exponent > 0) {
        if (exponent % 2 === 1) {
            result = (result * base) % modulus;
        }
        exponent = exponent >> 1;
        base = (base * base) % modulus;
    }
    return result;
}

class EllipticCurve {
    constructor(p, a, b, G, n) {
        this.p = p;
        this.a = a;
        this.b = b;
        this.G = G;
        this.n = n;
    }

        isOnCurve(P) {
        if (P === null) return true;
        const [x, y] = P;
        const left = (y * y) % this.p;
        const right = (x * x * x + this.a * x + this.b) % this.p;
        return left === right;
    }

    // Сложение точек на кривой
    addPoints(P, Q) {
        if (P === null) return Q;
        if (Q === null) return P;

        const [x1, y1] = P;
        const [x2, y2] = Q;

        if (x1 === x2 && y1 === y2) {
            // Удвоение точки
            if (y1 === 0) return null;
            const lambda = (3 * x1 * x1 + this.a) * modinv(2 * y1, this.p) % this.p;
            const x3 = (lambda * lambda - x1 - x2) % this.p;
            const y3 = (lambda * (x1 - x3) - y1) % this.p;
            return [this.modPositive(x3), this.modPositive(y3)];
        } else {
            if (x1 === x2) return null;
            const lambda = (y2 - y1) * modinv(x2 - x1, this.p) % this.p;
            const x3 = (lambda * lambda - x1 - x2) % this.p;
            const y3 = (lambda * (x1 - x3) - y1) % this.p;
            return [this.modPositive(x3), this.modPositive(y3)];
        }
    }

    // Умножение точки на скаляр (алгоритм "удвоение и сложение")
    multiplyPoint(k, P) {
        if (k === 0) return null;
        if (k === 1) return P;

        let R = null;
        let Q = P;
        let kTemp = k;

        while (kTemp > 0) {
            if (kTemp & 1) {
                R = this.addPoints(R, Q);
            }
            Q = this.addPoints(Q, Q);
            kTemp = kTemp >> 1;
        }
        return R;
    }

    // Приведение числа к положительному модулю
    modPositive(x) {
        const result = x % this.p;
        return result >= 0 ? result : result + this.p;
    }
}

const p = 17;   
const a = 2;
const b = 2;
const G = [5, 1];
const n = 19;   

const curve = new EllipticCurve(p, a, b, G, n);

function hashMessage(message) { 
    const gost = new GOST3411(256);
    const hashHex = gost.hashHex(message);
    
    // Преобразуем hex в число и берем по модулю n
    const hashBigInt = BigInt('0x' + hashHex);
    const hashInt = Number(hashBigInt % BigInt(n));
    
    return hashInt === 0 ? 1 : hashInt; 
}

function generateKeys() {
    const privateKey = Math.floor(Math.random() * (n - 1)) + 1;
    const publicKey = curve.multiplyPoint(privateKey, G);
    return { privateKey, publicKey };
}

function signMessage(privateKey, message) {
    const e = hashMessage(message);
    
    while (true) {
        const k = Math.floor(Math.random() * (n - 1)) + 1;
        const R = curve.multiplyPoint(k, G);
        
        if (R === null) continue;
        
        const r = R[0] % n;
        if (r === 0) continue;
        
        const kInv = modinv(k, n);
        const s = (kInv * (e + privateKey * r)) % n;
        
        if (s !== 0) {
            return { r, s };
        }
    }
}

function verifySignature(publicKey, message, signature) {
    const { r, s } = signature;
    
    if (!(0 < r && r < n && 0 < s && s < n)) {
        return false;
    }

    const e = hashMessage(message);
    const v = modinv(s, n);
    const z1 = (e * v) % n;
    const z2 = (r * v) % n;
    
    const C = curve.addPoints(
        curve.multiplyPoint(z1, G),
        curve.multiplyPoint(z2, publicKey)
    );
    
    if (C === null) {
        return false;
    }
    
    const R = C[0] % n;
    return R === r;
}

window.GOSTSignature = {
    curve,
    generateKeys,
    signMessage,
    verifySignature,
    hashMessage
};
