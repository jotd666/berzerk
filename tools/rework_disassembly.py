import re,collections,os

src = "../src/berzerk_z80.asm"

def is_hex(x):
    try:
        int(x,16)
        return True
    except ValueError:
        return False

with open(src) as f:
    lines = f.readlines()

labels = dict()
# collect labels
for i,line in enumerate(lines):
    m = re.match("(\w+):",line)
    if m:
        x = m.group(1)
        if not is_hex(x):
            real_address = None
            g = x.lower()
            address = g.rsplit("_")

            if len(address)>1:
                suffix = address[-1]
                if is_hex(suffix) and len(suffix)==4:
                    g = address[0]  # remove suffix
                    real_address = int(suffix,16)
            if not real_address:
                nextline = lines[i+1]
                m = re.match("(\w{4}):",nextline)
                if m:
                    real_address = int(m.group(1),16)
                else:
                    print(f"cannot compute address for {g}")
            labels[real_address] = g
            # set offset at the end of label name
            lines[i] = f"{g}_{real_address:04x}:\n"

# "call $xxxx  ; call function name" pattern associate if function name is in label list
for i,line in enumerate(lines):
    m = re.match(r"(.*\w\s+)call(.*)\$(\w+)(.*;.*)call\s+(\w+)(.*)",line)
    if m:
        prefix,cond,address,comment,name,rest = m.groups()

        name = name.lower()
        address = int(address,16)
        if address in labels:
            line = f"{prefix}call{cond}{labels[address]}_{address:04x}{comment}{rest}"
            line = line.strip(" ;")
            lines[i] = line+"\n"
        else:
            print(f"not found: {address:04x}, {name}")
    else:
        m = re.match(r"(.*\w\s+)call(.*)\$(\w+)(.*;.*)",line)
        if m:
            prefix,cond,address,comment = m.groups()
            address = int(address,16)
            if address in labels:
                line = f"{prefix}call{cond}{labels[address]}_{address:04x}{comment}"
                lines[i] = line+"\n"
            else:
                print(f"not found: {address:04x}")

with open(os.path.basename(src),"w") as f:
    f.writelines(lines)
