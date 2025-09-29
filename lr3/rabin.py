import random
from sympy import isprime
from typing import Tuple, List, Optional

class RabinServer:
    def __init__(self, key_size: int = 512):
        self.key_size = key_size
        self.p: Optional[int] = None
        self.q: Optional[int] = None
        self.n: Optional[int] = None
        self.yp: Optional[int] = None
        self.yq: Optional[int] = None
    
    def generate_keys(self) -> Optional[int]:
        while True:
            candidate = random.getrandbits(self.key_size)
            if isprime(candidate) and candidate % 4 == 3:
                self.p = candidate
                break
        
        while True:
            candidate = random.getrandbits(self.key_size)
            if (isprime(candidate) and candidate % 4 == 3 and 
                candidate != self.p):
                self.q = candidate
                break
        
        if self.p is not None and self.q is not None:
            self.n = self.p * self.q
            self._calculate_extended_euclidean()
            return self.n
        return None
    
    def _calculate_extended_euclidean(self) -> None:
        if self.p is None or self.q is None:
            raise ValueError("p и q должны быть инициализированы")
        
        a, b = self.p, self.q
        x0, x1, y0, y1 = 1, 0, 0, 1
        
        while b != 0:
            q_val = a // b
            a, b = b, a % b
            x0, x1 = x1, x0 - q_val * x1
            y0, y1 = y1, y0 - q_val * y1
        
        self.yp = x0
        self.yq = y0
    
    def encrypt(self, message: bytes) -> int:
        if self.n is None:
            raise ValueError("Ключи не сгенерированы")
        
        m = int.from_bytes(message, 'big')
                
        c = pow(m, 2, self.n)
        
        return c
    
    def decrypt(self, ciphertext: int) -> List[int]:
        if (self.p is None or self.q is None or 
            self.yp is None or self.yq is None or 
            self.n is None):
            raise ValueError("Приватные ключи не инициализированы")
        
        mp = self._mod_sqrt(ciphertext, self.p)
        mq = self._mod_sqrt(ciphertext, self.q)
        
        solutions = []
        for m_p in mp:
            for m_q in mq:
                r = (self.yp * self.p * m_q + self.yq * self.q * m_p) % self.n
                solutions.append(r)
                solutions.append(self.n - r)  # -r
                
                s = (self.yp * self.p * m_q - self.yq * self.q * m_p) % self.n
                solutions.append(s)
                solutions.append(self.n - s)  # -s
        
        solutions = list(set(solutions))
        
        print(solutions)
        
        return solutions
    
    def _mod_sqrt(self, a: int, p: int) -> List[int]:
        if p % 4 != 3:
            raise ValueError("Модуль должен быть вида 4k+3")
        
        exponent = (p + 1) // 4
        root = pow(a, exponent, p)
        
        return [root, p - root]
    
    def get_public_key(self) -> Optional[int]:
        return self.n
    
    def get_private_key(self) -> Optional[Tuple[int, int, int, int]]:
        if (self.p is not None and self.q is not None and 
            self.yp is not None and self.yq is not None):
            return (self.p, self.q, self.yp, self.yq)
        return None

def encrypt_file(input_file: str, output_file: str, public_key: RabinServer) -> None:
    with open(input_file, 'rb') as f:
        data = f.read()
    
    if public_key.n is None:
        raise ValueError("Публичный ключ не инициализирован")
    
    block_size = (public_key.n.bit_length() - 1) // 8
    encrypted_blocks = []
    
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        
        if len(block) < block_size:
            block = block + b'\x00' * (block_size - len(block))
        
        encrypted_block = public_key.encrypt(block)
        encrypted_blocks.append(str(encrypted_block))
    
    with open(output_file, 'w') as f:
        f.write(','.join(encrypted_blocks))

def decrypt_file(input_file: str, output_file: str, private_key: RabinServer) -> None:
    with open(input_file, 'r') as f:
        encrypted_blocks = [int(x) for x in f.read().split(',')]
    
    decrypted_data = b''
    block_size = (private_key.n.bit_length() - 1) // 8 if private_key.n else 0
    
    for block in encrypted_blocks:
        solutions = private_key.decrypt(block)
        
        solutions.sort(key=lambda x: x.bit_length(), reverse=False)
        
        correct_solution = None
        
        
        for solution in solutions:
            byte_data = (solution.bit_length() + 7) // 8
            print(byte_data)
            
            byte_data = solution.to_bytes(byte_data, 'big')
            print(byte_data)
            
            try:
                decoded = byte_data.decode('utf-8')
                print(decoded)
                correct_solution = byte_data
                #break
            except UnicodeDecodeError:
                print('error')
                continue
                    
        
        for solution in solutions:
            try:
                byte_data = solution.to_bytes(block_size, 'big')
                byte_data = byte_data.rstrip(b'\x00')
                
                try:
                    decoded = byte_data.decode('utf-8')
                    print(decoded)
                    correct_solution = byte_data
                    #break
                except UnicodeDecodeError:
                    print('error')
                    continue
                    
            except:
                continue
        
        if correct_solution is None:
            try:
                correct_solution = solutions[0].to_bytes(block_size, 'big').rstrip(b'\x00')
            except:
                correct_solution = b''
        
        decrypted_data += correct_solution
    
    with open(output_file, 'wb') as f:
        f.write(decrypted_data)
