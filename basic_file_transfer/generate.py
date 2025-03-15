def generate_file(filename, size_kb):
   
    content = "A" * 1024  # 1024 bytes of 'A', which is 1KB
    total_size = size_kb * 1024  
    num_chunks = total_size // len(content)  
    
    with open(filename, 'w') as file:
        for _ in range(num_chunks):
            file.write(content)
    
    print(f"File '{filename}' of size {size_kb} KB has been created.")

generate_file("large_file.txt", 1024)
