import hashlib

string = " Hi i am hash"

hashvalue = hashlib.sha256(string.encode())

print(hashvalue.hexdigest())


binary = "".join(f"{byte:08b}" for byte in hashvalue.digest())

print(binary)
print(len(binary))


def leading_zeros(bits: str) -> int:
    count = 0

    for bit in bits:
        if bit == "0":
            count += 1
        else:
            break

    return count


print("Leading zeros:", leading_zeros(binary))
