class GOST3411 {
    constructor(output_size = 512) {
        this.output_size = output_size;
        this.h = null;
        this.N = null;
        this.sigma = null;
        this._initConstants();
    }
    
    _initConstants() {
        if (this.output_size === 512) {
            this.h = 0x0064;  
        } else {
            this.h = 0x0164;  
        }
        
        this.N = 0;
        this.sigma = 0;
        
        this.S_BOX = [
            0xFC, 0xEE, 0xDD, 0x11, 0xCF, 0x6E, 0x31, 0x16,
            0xFB, 0xC4, 0xFA, 0xDA, 0x23, 0xC5, 0x04, 0x4D,
            0xE9, 0x77, 0xF0, 0xDB, 0x93, 0x2E, 0x99, 0xBA,
            0x17, 0x36, 0xF1, 0xBB, 0x14, 0xCD, 0x5F, 0xC1,
            0xF9, 0x18, 0x65, 0x5A, 0xE2, 0x5C, 0xEF, 0x21,
            0x81, 0x1C, 0x3C, 0x42, 0x8B, 0x01, 0x8E, 0x4F,
            0x05, 0x84, 0x02, 0xAE, 0xE3, 0x6A, 0x8F, 0xA0,
            0x06, 0x0B, 0xED, 0x98, 0x7F, 0xD4, 0xD3, 0x1F,
            0xEB, 0x34, 0x2C, 0x51, 0xEA, 0xC8, 0x48, 0xAB,
            0xF2, 0x2A, 0x68, 0xA2, 0xFD, 0x3A, 0xCE, 0xCC,
            0xB5, 0x70, 0x0E, 0x56, 0x08, 0x0C, 0x76, 0x12,
            0xBF, 0x72, 0x13, 0x47, 0x9C, 0xB7, 0x5D, 0x87,
            0x15, 0xA1, 0x96, 0x29, 0x10, 0x7B, 0x9A, 0xC7,
            0xF3, 0x91, 0x78, 0x6F, 0x9D, 0x9E, 0xB2, 0xB1,
            0x32, 0x75, 0x19, 0x3D, 0xFF, 0x35, 0x8A, 0x7E,
            0x6D, 0x54, 0xC6, 0x80, 0xC3, 0xBD, 0x0D, 0x57,
            0xDF, 0xF5, 0x24, 0xA9, 0x3E, 0xA8, 0x43, 0xC9,
            0xD7, 0x79, 0xD6, 0xF6, 0x7C, 0x22, 0xB9, 0x03,
            0xE0, 0x0F, 0xEC, 0xDE, 0x7A, 0x94, 0xB0, 0xBC,
            0xDC, 0xE8, 0x28, 0x50, 0x4E, 0x33, 0x0A, 0x4A,
            0xA7, 0x97, 0x60, 0x73, 0x1E, 0x00, 0x62, 0x44,
            0x1A, 0xB8, 0x38, 0x82, 0x64, 0x9F, 0x26, 0x41,
            0xAD, 0x45, 0x46, 0x92, 0x27, 0x5E, 0x55, 0x2F,
            0x8C, 0xA3, 0xA5, 0x7D, 0x69, 0xD5, 0x95, 0x3B,
            0x07, 0x58, 0xB3, 0x40, 0x86, 0xAC, 0x1D, 0xF7,
            0x30, 0x37, 0x6B, 0xE4, 0x88, 0xD9, 0xE7, 0x89,
            0xE1, 0x1B, 0x83, 0x49, 0x4C, 0x3F, 0xF8, 0xFE,
            0x8D, 0x53, 0xAA, 0x90, 0xCA, 0xD8, 0x85, 0x61,
            0x20, 0x71, 0x67, 0xA4, 0x2D, 0x2B, 0x09, 0x5B,
            0xCB, 0x9B, 0x25, 0xD0, 0xBE, 0xE5, 0x6C, 0x52,
            0x59, 0xA6, 0x74, 0xD2, 0xE6, 0xF4, 0xB4, 0xC0,
            0xD1, 0x66, 0xAF, 0xC2, 0x39, 0x4B, 0x63, 0xB6
        ];
        
        this.C = [];
        for (let i = 0; i < 12; i++) {
            this.C.push(this._generateC(i));
        }
    }
    
    _generateC(i) {
        return (BigInt(i) * 0x0123456789ABCDEFn) & ((1n << 512n) - 1n);
    }
    
    _xTransform(a, b) {
        /* X-преобразование: XOR двух 512-битных последовательностей */
        return a ^ b;
    }
    
    _sTransform(data) {
        /* S-преобразование: подстановка байтов */
        let result = 0n;
        for (let i = 0; i < 64; i++) {
            const byteVal = Number((data >> BigInt(i * 8)) & 0xFFn);
            const substituted = BigInt(this.S_BOX[byteVal]);
            result |= substituted << BigInt(i * 8);
        }
        return result;
    }
    
    _pTransform(data) {
        /* P-преобразование. Функция перестановки */
        const bytesList = [];
        for (let i = 0; i < 64; i++) {
            bytesList.push(Number((data >> BigInt(i * 8)) & 0xFFn));
        }
        
        const permuted = new Array(64).fill(0);
        for (let i = 0; i < 64; i++) {
            permuted[i] = bytesList[(i * 7) % 64];
        }
        
        let result = 0n;
        for (let i = 0; i < 64; i++) {
            result |= BigInt(permuted[i]) << BigInt(i * 8);
        }
        return result;
    }
    
    _lTransform(data) {
        /** L-преобразование: умножение 64-битного вектора на матрицу A 64x64 */
        let result = 0n;
        
        for (let blockIdx = 0; blockIdx < 8; blockIdx++) {
            const blockStart = blockIdx * 64;
            const blockData = (data >> BigInt(blockStart)) & 0xFFFFFFFFFFFFFFFFn;
            
            const transformedBlock = this._lTransformBlock(blockData);
            
            result |= transformedBlock << BigInt(blockStart);
        }
        
        return result;
    }
    
    _lTransformBlock(block) {
        const A_MATRIX = [
            0x8e20faa72ba0b470n, 0x6c022c38f90a4c07n, 0xa0116380818e8f40n, 0x0ad97808d06cb404n,
            0x90dab52a387ae76fn, 0x092e94218d243cban, 0x9d4df05d5f661451n, 0x18150f14b9ec46ddn,
            0x86275df09ce8aaa8n, 0xe230140fc0802984n, 0x456c34887a3805b9n, 0x9bcf4486248d9f5dn,
            0xe4fa2054a80b329cn, 0x492c024284fbaec0n, 0x70a6a56e2440598en, 0x07e095624504536cn,
            0x47107ddd9b505a38n, 0x3601161cf205268dn, 0x5086e740ce47c920n, 0x05e23c0468365a02n,
            0x486dd4151c3dfdb9n, 0x8a174a9ec8121e5dn, 0xc0a878a0a1330aa6n, 0x0c84890ad27623e0n,
            0x439da0784e745554n, 0x71180a8960409a42n, 0xac361a443d1c8cd2n, 0xc3e9224312c8c10an,
            0x727d102a548b194en, 0xaa16012142f35760n, 0x3853dc371220a247n, 0x8d70c431ac02a736n,
            0xad08b0e0c3282d1cn, 0x1b8e0b0e798c13c8n, 0x2843fd2067adea10n, 0x8c711e02341b2d01n,
            0x24b86a840e90f0d2n, 0x4585254f64090fa0n, 0x60543c50de970553n, 0x0642ca05693b9f70n,
            0xafc0503c273aa42an, 0xb60c05ca30204d21n, 0x561b0d22900e4669n, 0xeffa11af0964ee50n,
            0x39b008152acb8227n, 0x550b8e9e21f7a530n, 0x1ca76e95091051adn, 0xc83862965601dd1bn,
            0xd8045870ef14980en, 0x83478b07b2468764n, 0x14aff010bdd87508n, 0x46b60f011a83988en,
            0x125c354207487869n, 0xaccc9ca9328a8950n, 0x302a1e286fc58ca7n, 0x0321658cba93c138n,
            0xd960281e9d1d5215n, 0x5b068c651810a89en, 0x2b838811480723ban, 0xf97d86d98a327728n,
            0x9258048415eb419dn, 0xa48b474f9ef5dc18n, 0x0edd37c48a08a6d8n, 0x641c314b2b8ee083n
        ];
        
        let result = 0n;
        
        for (let i = 0; i < 64; i++) {
            if (this._matrixMultiplyBit(block, A_MATRIX[i])) {
                result |= (1n << BigInt(63 - i));
            }
        }
        
        return result;
    }
    
    _matrixMultiplyBit(vector, matrixRow) {
        let product = vector & matrixRow;
        
        let parity = 0;
        while (product > 0n) {
            parity ^= Number(product & 1n);
            product >>= 1n;
        }
        
        return parity;
    }
    
    _keySchedule(k, i) {
        k = this._xTransform(k, this.C[i]);
        k = this._sTransform(k);
        k = this._pTransform(k);
        k = this._lTransform(k);
        return k;
    }
    
    _eFunction(k, m) {
        let state = this._xTransform(k, m);
        
        for (let i = 0; i < 12; i++) {
            state = this._sTransform(state);
            state = this._pTransform(state);
            state = this._lTransform(state);
            k = this._keySchedule(k, i);
            state = this._xTransform(state, k);
        }
        
        return state;
    }
    
    _compressionFunction(n, m, h) {
        /** Функция сжатия g(N, m, h) */
        // Шаги 1-4
        let k = this._xTransform(h, n);
        k = this._sTransform(k);
        k = this._pTransform(k);
        k = this._lTransform(k);
        
        // Шаг 5
        let t = this._eFunction(k, m);
        
        // Шаг 6
        t = this._xTransform(h, t);
        
        // Шаг 7
        let g = this._xTransform(t, m);
        
        return g;
    }
    
    _padMessage(message) {
        let msgBytes;
        
        if (typeof message === 'string') {
            const encoder = new TextEncoder();
            msgBytes = encoder.encode(message);
        } else {
            msgBytes = message;
        }
        
        const msgLen = msgBytes.length * 8;
        
        let msgInt = 0n;
        for (let i = 0; i < msgBytes.length; i++) {
            msgInt = (msgInt << 8n) | BigInt(msgBytes[i]);
        }
        
        let paddingLen = 511 - (msgLen % 512);
        if (paddingLen === 511) {
            paddingLen = 0;
        }
        
        const padded = (msgInt << BigInt(paddingLen + 1)) | (1n << BigInt(paddingLen));
        
        return [padded, msgLen];
    }
    
    hash(message) {
        let h = this.output_size === 512 ? 0x0064n : 0x0164n;
        
        let n = 0n;
        let sigma = 0n;
        
        const [paddedMsg, msgLen] = this._padMessage(message);
        
        let tempMsg = paddedMsg;                
        while (tempMsg > 0n) {
            const m = tempMsg & ((1n << 512n) - 1n);
            tempMsg >>= 512n;
            
            if (tempMsg === 0n && m === 0n) {
                break;
            }
            
            h = this._compressionFunction(n, m, h);
            n = (n + 512n) % (1n << 512n);
            sigma = (sigma + m) % (1n << 512n);
        }
        
        h = this._compressionFunction(0n, h, n);
        h = this._compressionFunction(0n, h, sigma);
        
        if (this.output_size === 256) {
            h = h >> 256n;
        }
        
        return h;
    }
    
    hashHex(message) {
        let hashValue = this.hash(message);
        
        const bitMask = (1n << BigInt(this.output_size)) - 1n;
        hashValue = hashValue & bitMask;
        
        const hexLen = this.output_size / 4;
        let hexString = hashValue.toString(16).padStart(hexLen, '0');
        
        return hexString;
    }
}
