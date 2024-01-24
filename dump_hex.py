import argparse
import os
import time

def split_list(lst):
    half = len(lst) // 2
    return [lst[:half], lst[half:]]

def pad_list(lst, length):
    return lst + ["00"] * (length - len(lst))

def format_address(address, total_bytes):
    address_width = len(hex(total_bytes - 1)[2:])
    pad_width = max(0, 8 - address_width)
    return f"{'0' * pad_width}{address:0{address_width}X}"

def parse_file(file_path: str, output_path: str):
    file_bytes = []
    bytes_wrote = 0
    address = 0
    first_line = True

    start = time.time()
    with open(file_path, 'rb') as f:
        total_bytes = 0
        for chunk in iter(lambda: f.read(16), b''):
            total_bytes += len(chunk)

        f.seek(0)

        print(f"[+] Reading {total_bytes} bytes from {file_path}")
        for chunk in iter(lambda: f.read(16), b''):
            info = [chunk[i:i+1].hex().upper() for i in range(0, len(chunk), 1)]
            bytes_ = split_list(info)
            bytes_[0] = pad_list(bytes_[0], 8)
            bytes_[1] = pad_list(bytes_[1], 8)
            file_bytes.append((format_address(address, total_bytes), bytes_))
            address += 16

    end = time.time()

    print(f"[+] Read {total_bytes} bytes from {file_path} in {end - start:.2f} seconds")


    decoded_ascii = []

    for _, data in file_bytes:
        ascii_ = []
        for byte in data[0] + data[1]:
            ascii_.append(chr(int(byte, 16)))
        decoded_ascii.append("".join(ascii_).replace("\n", "").replace("\r", "").replace("\t", ""))

    start = time.time()
    with open(output_path, "w", encoding="utf-8") as f:
        for i, (addr, data) in enumerate(file_bytes):
            if first_line:
                bytes_wrote += f.write(f"Dumped using a Lapis Pheonix Tool\nFile: {file_path}\n\n")
                bytes_wrote += f.write("Address:   Bytes 1-8                Bytes 9-16               ASCII\n")
                first_line = False
            bytes_wrote += f.write(f"{addr}:  {' '.join(data[0])}  {' '.join(data[1])}  {decoded_ascii[i]}\n")
    end = time.time()

    print(f"[+] Wrote {bytes_wrote} bytes to {output_path} in {end - start:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file to dump", default=None, nargs="?")
    parser.add_argument("-d", "--directory", help="directory to batch dump")
    parser.add_argument("-o", "--output", help="output file")

    args = parser.parse_args()

    file = args.file
    directory = args.directory
    output = args.output

    if directory:
        if not os.path.exists(os.path.join(directory, "dumped")):
            os.makedirs(os.path.join(directory, "dumped"))
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path):
                output_path = os.path.join(directory, "dumped", file_name + ".txt")
                parse_file(file_path, output_path)
    else:
        parse_file(file, output)
