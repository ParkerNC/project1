
import math
import sys
from time import time

reads = 0
writes = 0

pageRef = 0
diskRef = 0


class TLB():
    def __init__(self, setNum: int = 256, ass: int = 8, active: bool = True, cache: list = [], index: int = 0) -> None:
        self.setNum = setNum
        self.ass = ass
        self.active = active
        self.cache = cache
        self.index = index
        self.hits = 0
        self.miss = 0

class DC():
    def __init__(self, setNum: int = 8192, ass: int = 8, block_size: int = 8, write_back: bool = True, cache: list = [], index: int = 0, offset: int = 0) -> None:
        self.setNum = setNum
        self.ass = ass
        self.blockSize = block_size
        self.writeBack = write_back
        self.cache = cache
        self.index = index
        self.offset = offset
        self.dirty = False
        self.hits = 0
        self.miss = 0
        self.ref = 0

class L2():
    def __init__(self, setNum: int = 8192, ass: int = 8, active: bool = True, block_size: int = 8, write_back: bool = True, cache: list = [], index: int = 0, offset: int = 0) -> None:
        self.setNum = setNum
        self.ass = ass
        self.blockSize = block_size
        self.writeBack = write_back
        self.active = active
        self.cache = cache
        self.index = index
        self.offset = offset
        self.dirty = True
        self.hits = 0
        self.miss = 0
        self.ref = 0


class PT():
    def __init__(self, physicalPages: int = 1024, virtualPages: int = 8192, page_size: int = 0, active: bool = True, index: int = 0, offset: int = 0) -> None:
        self.pPages = physicalPages
        self.vPages = virtualPages
        self.pageSize = page_size
        self.active = active
        self.vcache = []
        self.pcache = []
        self.index = index
        self.offset = offset
        self.hits = 0
        self.miss = 0




def initialize(tlb: TLB, dc: DC, l2: L2, pt: PT, file: list) -> None:

    for i, opt in enumerate(file):
        if "Data TLB configuration" in opt:
            if "Number of sets:" in file[i+1]:
                tlb.setNum = int(file[i+1].split(": ")[1])
                if tlb.setNum > 256:
                    print("hierarchy: error - number of dtlb sets requested exceeds MAXTLBSETS", file=sys.stderr)
                    exit(2)
                if (tlb.setNum & (tlb.setNum-1) != 0) or tlb.setNum == 0:
                    print("hierarchy: number of dtlb sets is not a power of two", file=sys.stderr)
                    exit(2)
                print(f"Data TLB contains {tlb.setNum} sets.")
            if "Set size:" in file[i+ 2]:
                tlb.ass = int(file[i+2].split(": ")[1])
                if tlb.ass > 8:
                    print("hierarchy: error - dtlb set size requested exceeds MAXSETSIZE", file=sys.stderr)
                    exit(2)
                print(f"Each set contains {tlb.ass} entries.")


            tlb.index = int(math.log(tlb.setNum, 2))
            print(f"Number of bits used for the index is {tlb.index}.")
            print("")
        
        elif "Page Table configuration" in opt:
            if "Number of virtual pages:" in file[i+1]:
                pt.vPages = int(file[i+1].split(": ")[1])
                if pt.vPages > 8192:
                    print("hierarchy: error - number of virtual pages requested exceeds MAXVIRTPAGES", file=sys.stderr)
                    exit(2)
                if (pt.vPages & (pt.vPages-1) != 0) or pt.vPages == 0:
                    print("hierarchy: number of virtual pages is not a power of two", file=sys.stderr)
                    exit(2)
                print(f"Number of virtual pages is {pt.vPages}.")
            if "Number of physical pages:" in file[i+2]:
                pt.pPages = int(file[i+2].split(": ")[1])
                if pt.pPages > 1024:
                    print("hierarchy: error - number of physical pages requested exceeds MAXPHYPAGES", file=sys.stderr)
                    exit(2)
                if (pt.pPages & (pt.pPages-1) != 0) or pt.pPages == 0:
                    print("hierarchy: number of physical pages is not a power of two", file=sys.stderr)
                    exit(2)
                print(f"Number of physical pages is {pt.pPages}.")
            if "Page size:" in file[i+3]:
                pt.pageSize = int(file[i+3].split(": ")[1])
                if (pt.pageSize & (pt.pageSize-1) != 0) or pt.pageSize == 0:
                    print("hierarchy: page size is not a power of two", file=sys.stderr)
                    exit(2)
                print(f"Each page contains {pt.pageSize} bytes.")

            pt.index = int(math.log(pt.vPages, 2))
            print(f"Number of bits used for the page table index is {pt.index}.")

            pt.offset = int(math.log(pt.pageSize, 2))
            print(f"Number of bits used for the page offset is {pt.offset}.")
            print("")
        
        elif "Data Cache configuration" in opt:
            if "Number of sets:" in file[i+1]:
                dc.setNum = int(file[i+1].split(": ")[1])
                if dc.setNum > 8192:
                    print("hierarchy: error - number of dc sets requested exceeds MAXDCSETS", file=sys.stderr)
                    exit(2)
                if (dc.setNum & (dc.setNum-1) != 0) or dc.setNum == 0:
                    print("hierarchy: number of dc sets is not a power of two", file=sys.stderr)
                    exit(2)
                print(f"D-cache contains {dc.setNum} sets.")
            if "Set size:" in file[i+2]:
                dc.ass = int(file[i+2].split(": ")[1])
                if dc.ass > 8:
                    print("hierarchy: error - data cache set size requested exceeds MAXSETSIZE", file=sys.stderr)
                    exit(2)
                print(f"Each set contains {dc.ass} entries.")
            if "Line size:" in  file[i+3]:
                dc.blockSize = int(file[i+3].split(': ')[1])
                if (dc.blockSize & (dc.blockSize-1) != 0) or dc.blockSize == 0:
                    print("hierarchy: number of bytes in dc line is not a power of two", file=sys.stderr)
                    exit(2)
                print(f"Each line is {dc.blockSize} bytes.")
            if "Write through" in file[i+4]:
                if "n" in file[i+4].split(": ")[1]:
                    dc.writeBack = True
                    print("The cache uses a write-allocate and write-back policy.")
                else:
                    dc.writeBack = False
                    print("The cache uses a no write-allocate and write-through policy.")

            dc.index = int(math.log(dc.setNum, 2))
            print(f"Number of bits used for the index is {dc.index}.")

            dc.offset = int(math.log(dc.blockSize, 2))
            print(f"Number of bits used for the offset is {dc.offset}.")
            print("")

        elif "L2 Cache configuration" in opt:
            if "Number of sets:" in file[i+1]:
                l2.setNum = int(file[i+1].split(": ")[1])
                if (l2.setNum & (l2.setNum-1) != 0) or l2.setNum == 0:
                    print("hierarchy: number of L2 sets is not a power of two", file=sys.stderr)
                    exit(2)
                print(f"L2-cache contains {l2.setNum} sets.")
            if "Set size:" in file[i+2]:
                l2.ass = int(file[i+2].split(": ")[1])
                if l2.ass > 8:
                    print("hierarchy: error - L2 cache set size requested exceeds MAXSETSIZE", file=sys.stderr)
                    exit(2)
                print(f"Each set contains {l2.ass} entries.")
            if "Line size:" in  file[i+3]:
                l2.blockSize = int(file[i+3].split(': ')[1])
                if (dc.blockSize > l2.blockSize):
                    print("hierarchy: L2 cache line size must be >= to the data cache line size", file=sys.stderr)
                    exit(2)
                if (l2.blockSize & (l2.blockSize-1) != 0) or l2.blockSize == 0:
                    print("hierarchy: number of bytes in L2 line is not a power of two", file=sys.stderr)
                    exit(2)
                print(f"Each line is {l2.blockSize} bytes.")
            if "Write through" in file[i+4]:
                if "n" in file[i+4].split(": ")[1]:
                    l2.writeBack = True
                    print("The cache uses a write-allocate and write-back policy.")
                else:
                    l2.writeBack = False
                    print("The cache uses a no write-allocate and write-through policy.")

            l2.index = int(math.log(l2.setNum, 2))
            print(f"Number of bits used for the index is {l2.index}.")

            l2.offset = int(math.log(l2.blockSize, 2))
            print(f"Number of bits used for the offset is {l2.offset}.")
            print("")
        
        elif "Virtual addresses" in opt:
            if "y" in opt.split(": ")[1]:
                pt.active = True
                print("The addresses read in are virtual addresses.")
            else:
                pt.active = False
                print("The addresses read in are physical addresses.")


        elif "TLB:" in opt:
            if "y" in opt.split(": ")[1]:
                tlb.active = True
                if tlb.active == True and pt.active == False:
                    print("hierarchy: TLB cannot be enabled when virtual addresses are disabled", file=sys.stderr)
                    exit(2)
            else:
                tlb.active = False     
                print("TLB is disabled in this configuration.")

        elif "L2 cache:" in opt:
            if "y" in opt.split(": ")[1]:
                l2.active = True
            else:
                l2.active = False
                print("L2 cache is disabled in this configuration.")

    dc.cache = [ [-1]*dc.ass for _ in range(dc.setNum) ]

    l2.cache = [ [-1]*l2.ass for _ in range(l2.setNum) ]

    pt.pcache = [ -1 for _ in range(pt.pPages)]
    pt.vcache = [ -1 for _ in range(pt.vPages)]

    tlb.cache = [ [-1]*tlb.ass for _ in range(tlb.setNum) ]
    
    print("")

def dcOnly(dc: DC, address: int, type: str, offset: int, t: int, access, l2: L2, l2access) -> str:

    dcTag = address >> (dc.index + dc.offset)

    dcIndexMask = (1 << dc.index) -1

    dcIndex = (address >> dc.offset) & dcIndexMask

    result = access(dc, address, dcTag, offset, dcIndex, type, t)

    dcRes = ""

    if result:
        dcRes = "hit"
    else:
        dcRes = "miss"
        

    return dcTag, dcIndex, dcRes, "", "", ""
    

def l2dc(dc: DC, address: int, type: str, offset: int,  t: int, access, l2: L2, l2access) -> list:
    dcTag = address >> (dc.index + dc.offset)

    dcIndexMask = (1 << dc.index) -1

    dcIndex = (address >> dc.offset) & dcIndexMask

    l2Tag = address >> (l2.index + l2.offset)

    l2IndexMask = (1 << l2.index) -1

    l2Index = (address >> l2.offset) & l2IndexMask

    result = access(dc, address, dcTag, offset, dcIndex, type, t)

    dcRes = ""
    l2Res = ""

    if result:
        dcRes = "hit"
        
        if not dc.writeBack and type == "W":
            l2result = l2access(l2, address, l2Tag, offset, l2Index, type, t)
            if l2result:
                l2Res = "hit"
            else:
                l2Res = "miss"
        
    else:
        dcRes = "miss"
        l2result = l2access(l2, address, l2Tag, offset, l2Index, type, t)
        if l2result:
            l2Res = "hit"
        else:
            l2Res = "miss"

        if dc.dirty:
            l2.hits +=1
            dc.dirty = False
        """
        if not dc.writeBack:
            l2result = l2access(l2, address, l2Tag, offset, l2Index, type, t)
            if l2result:
                l2Res = "hit"
            else:
                l2Res = "miss"
        if dc.writeBack:
            if dc.dirty:
                l2result = l2access(l2, address, l2Tag, offset, l2Index, type, t)
                if l2result:
                    l2Res = "hit"
                else:
                    l2Res = "miss"
                dc.dirty = False
            else:
                dryResult = dryAccess(l2, address, l2Tag, offset, l2Index, type, t)
                if dryResult:
                    l2Res = "hit"
                else:
                    l2Res = "miss"

        """


    return dcTag, dcIndex, dcRes, l2Tag, l2Index, l2Res    

def ptAcess(pt: PT, address: int, typ: str, offset: int, t: int, tlb) -> list:

    vTag = address >> (pt.index + pt.offset)  
    vIndexMask = (1 << dc.index) -1
    vIndex = (address >> pt.offset) & vIndexMask
    vpn = address >> pt.offset
    vRes = ""
    pPageNum = -1
    tlbIndex = ""
    tlbTag = ""
    tlbRes = ""
    global pageRef
    global diskRef


    vcacheNum = vIndex % len(pt.vcache)
    if pt.vcache[vcacheNum] == -1:
        pt.vcache[vcacheNum] = vTag
    elif pt.vcache[vcacheNum] == vTag:
        pt.vcache[vcacheNum] = vTag

    if tlb.active:
        tlbRes, tlbTag, tlbIndex = tlbaccess(tlb, pt, address, offset, t)
        if tlbRes == "hit":
            for i, page in enumerate(pt.pcache):
                if page[0] == vpn:
                    pt.pcache[i] = (vpn, t)
                    pPageNum = i
                    break

            pAdd = address & ((1 << pt.offset)-1)
            pAdd = (pPageNum << pt.offset) | pAdd
            return pAdd, pPageNum, vpn, vRes, tlbRes, tlbTag, tlbIndex

    old = t
    pageRef +=1

    for i, page in enumerate(pt.pcache):
        if page == -1:
            vRes = "miss"
            diskRef +=1
            pt.miss +=1 
            pt.pcache[i] = (vpn, t)
            pPageNum = i
            break
        elif page[0] == vpn:
            pt.hits +=1
            pt.pcache[i] = (vpn, t)
            pPageNum = i
            vRes = "hit"
            break
        else:
            if old > page[1]:
                old = page[1]
    
    if pPageNum != -1:
        pAdd = address & ((1 << pt.offset)-1)
        pAdd = (pPageNum << pt.offset) | pAdd
        return pAdd, pPageNum, vpn, vRes, tlbRes, tlbTag, tlbIndex
    
    for i, page in enumerate(pt.pcache): 
        if page[1] == old:
            pt.pcache[i] = (vpn, t)
            pt.miss +=1
            diskRef +=1
            vRes = "miss"
            pAdd = address & ((1 << pt.offset)-1)
            pAdd = (pPageNum << pt.offset) | pAdd
            break

    return pAdd, pPageNum, vpn, vRes, tlbRes, tlbTag, tlbIndex

def tlbaccess(tlb: TLB, pt: PT, address: int, offset: int, t) -> list:
    tag = address >> (tlb.index + pt.offset)

    IndexMask = (1 << tlb.index) -1

    index = (address >> pt.offset) & IndexMask
    blockNum = index % len(tlb.cache)
    old = t

    for i, bSet in enumerate(tlb.cache[blockNum]):        
        if bSet == -1:
            tlb.cache[blockNum][i] = (tag, index, t)
            tlb.miss +=1
            return "miss", tag, index
        elif bSet[0] == tag:
            tlb.hits +=1
            tlb.cache[blockNum][i] = (tag, index, t)
            return "hit", tag, index
        else:
            if old > bSet[2]:
                old = bSet[2]

    for i, bSet in enumerate(tlb.cache[blockNum]):
        if bSet[2] == old:
            tlb.miss +=1
            tlb.cache[blockNum][i] = (tag, index, t)
            return "miss", tag, index

def dryAccess(dc: DC, address: int, tag: int, offset: int, index: int, type: str, t: float) -> bool:
    blockNum = index % len(dc.cache)
    old = t

    for i, bSet in enumerate(dc.cache[blockNum]):        
        if bSet == -1:
            dc.miss +=1
            return False
        elif bSet[0] == tag:
            dc.cache[blockNum][i] = (tag, index, offset, t, False)
            dc.hits +=1
            return True
        else:
            if old > bSet[3]:
                old = bSet[3]
    
    dc.miss +=1
    return False

def accessWriteBack(dc: DC, address: int, tag: int, offset: int, index: int, type: str, t: float) -> bool:


    blockNum = index % len(dc.cache)
    old = t

    for i, bSet in enumerate(dc.cache[blockNum]):        
        if bSet == -1:
            dc.cache[blockNum][i] = (tag, index, offset, t, True)
            #if type == "W":
            #    dc.cache[blockNum][i] = (tag, index, offset, t, True)
            dc.ref +=1
            dc.miss +=1
            return False
        elif bSet[0] == tag:
            dc.cache[blockNum][i] = (tag, index, offset, t, False)
            if type == "W":
                dc.cache[blockNum][i] = (tag, index, offset, t, True)
            dc.hits +=1
            return True
        else:
            if old > bSet[3]:
                old = bSet[3]

    for i, bSet in enumerate(dc.cache[blockNum]):
        if bSet[3] == old:
            if bSet[4]:
                dc.dirty = True
                dc.ref +=1
            dc.cache[blockNum][i] = (tag, index, offset, t, False)
            if type == "W":
                dc.cache[blockNum][i] = (tag, index, offset, t, True)
            
            dc.ref+=1
            dc.miss +=1
            return False


        
def accessWriteThrough(dc: DC, address: int, tag: int, offset: int, index: int, type: str, t: float) -> int:
    blockNum = index % len(dc.cache)
    t = time()
    old = t

    for i, bSet in enumerate(dc.cache[blockNum]):        
        if bSet == -1:
            if type == "W":
                dc.miss +=1
                dc.ref +=1
                return 0
            dc.miss +=1
            dc.ref +=1
            dc.cache[blockNum][i] = (tag, index, offset, t)
            return 0
        elif bSet[0] == tag:
            if type == "W":
                dc.ref +=1
            dc.hits +=1
            dc.cache[blockNum][i] = (tag, index, offset, t)
            return 1
        else:
            if old > bSet[3]:
                old = bSet[3]

    if type == "W":
        dc.miss +=1
        dc.ref +=1
        return 0

    for i, bSet in enumerate(dc.cache[blockNum]):
        if bSet[3] == old:
            dc.miss +=1
            dc.ref +=1
            dc.cache[blockNum][i] = (tag, index, offset, t)
            return 0

if __name__ == "__main__":
    options = []
    with open("trace.config", "r") as configFile:
        for setting in configFile:
            options.append(setting)

    tlb = TLB()
    dc = DC()
    l2 = L2()
    pt = PT()
    
    initialize(tlb, dc, l2, pt, options)

    dcAccess = None

    l2Access = None

    if l2.writeBack:
        l2Access = accessWriteBack
    else:
        l2Access = accessWriteThrough
        if dc.writeBack:
            l2Access = accessWriteBack

    if dc.writeBack:
        dcAccess = accessWriteBack
    else:
        dcAccess = accessWriteThrough



    accessfunction = dcOnly

    if l2.active:
        accessfunction = l2dc

    add = "Virtual"
    if pt.active == False:
        add = "Physical"

    print(f"{add:<8} {'Virt.':<6} {'Page':<4} {'TLB':<6} {'TLB':<3} {'TLB':<4} {'PT':<4} {'Phys':<4} {' ':<6} {'DC':<3} {'DC':<4} {' ':<6} {'L2':<3} {'L2':<4}")
    print(f"{'Address':<8} {'Page #':<6} {'Off':<4} {'Tag':<6} {'Ind':<3} {'Res.':<4} {'Res.':<4} {'Pg #':<4} {'DC Tag':<6} {'Ind':<3} {'Res.':<4} {'L2 Tag':<6} {'Ind':<3} {'Res.':<4}")
    print(f"{'-'*8} {'-'*6} {'-'*4} {'-'*6} {'-'*3} {'-'*4} {'-'*4} {'-'*4} {'-'*6} {'-'*3} {'-'*4} {'-'*6} {'-'*3} {'-'*4}")

    for access in sys.stdin:
        acc = access.strip()
        acc = acc.split(":")
        address = acc[1]
        acctype = acc[0]
        addNum = int(address, 16)

        if (addNum >> pt.offset) > pt.pageSize or (addNum >> pt.index + pt.offset):
            print(f"hierarchy: virtual address {hex(addNum)[2:]} is too large", file=sys.stderr)
            exit(2)

        pageMask = (1 << pt.offset) - 1
        pageOffset = addNum & pageMask
        pPageNum = (addNum >> pt.offset)

        if acctype == "R":
            reads += 1
        elif acctype == "W":
            writes +=1 
        else:
            print("hierarchy: unexpected access type", file=sys.stderr)
            exit(2)

        t = time()

        vPageNum = ""
        ptRes = ""
        tlbRes = ""
        tlbTag = ""
        tlbIndex = ""

        if pt.active:
            addNum, pPageNum, vPageNum, ptRes, tlbRes, tlbTag, tlbIndex = ptAcess(pt, addNum, acctype, pageOffset, t, tlb)
            vPageNum = hex(vPageNum)[2:]
            if tlb.active:
                tlbTag = hex(tlbTag)[2:]
                tlbIndex = hex(tlbIndex)[2:]

        dcTag, dcIndex, dcRes, strl2Tag, strl2Index, l2Res = accessfunction(dc, addNum, acctype, pageOffset, t, dcAccess, l2, l2Access)

        if l2Res == "":
            strl2Index = ""
            strl2Tag = ""
        else:
            strl2Tag = hex(strl2Tag)[2:]
            strl2Index = hex(strl2Index)[2:]


        print(f"{address:0>8} {vPageNum:>6} {hex(pageOffset)[2:]:>4} {tlbTag:>6} {tlbIndex:>3} {tlbRes:<4} {ptRes:<4} {hex(pPageNum)[2:]:>4} {hex(dcTag)[2:]:>6} {hex(dcIndex)[2:]:>3} {dcRes:<4} {strl2Tag:>6} {strl2Index:>3} {l2Res:<4}")


    print("")
    print("Simulation statistics")
    print("")

    print(f"{'dtlb hits':<17}: {tlb.hits}")
    print(f"{'dtlb misses':<17}: {tlb.miss}")
    dtlbRat = "N/A"
    if tlb.active:
        dtlbRat = tlb.hits/(tlb.miss + tlb.hits)
        print(f"{'dtlb hit ratio':<17}: {dtlbRat:6f}")
    else:
        print(f"{'dtlb hit ratio':<17}: {dtlbRat}")
    print("")
    
    print(f"{'pt hits':<17}: {pt.hits}")
    print(f"{'pt faults':<17}: {pt.miss}")
    ptRat = "N/A"
    if pt.active:
        ptRat = pt.hits/(pt.miss + pt.hits)
        print(f"{'pt hit ratio':<17}: {ptRat:6f}")
    else:
        print(f"{'pt hit ratio':<17}: {ptRat}")
    print("")

    print(f"{'dc hits':<17}: {dc.hits}")
    print(f"{'dc misses':<17}: {dc.miss}")
    dcRat = dc.hits/(dc.miss + dc.hits)
    print(f"{'dc hit ratio':<17}: {dcRat:6f}")
    print("")

    print(f"{'L2 hits':<17}: {l2.hits}")
    print(f"{'L2 misses':<17}: {l2.miss}")
    l2Rat = "N/A"
    if l2.active:
        l2Rat = l2.hits/(l2.miss + l2.hits)
        print(f"{'L2 hit ratio':<17}: {l2Rat:6f}")
    else:
        print(f"{'L2 hit ratio':<17}: {l2Rat}")
    print("")

    print(f"{'Total reads':<17}: {reads}")
    print(f"{'Total writes':<17}: {writes}")
    rwRat = reads/(reads + writes)
    print(f"{'Ratio of reads':<17}: {rwRat:6f}")
    print("")

    mainRef = dc.ref
    if l2.active:
        mainRef = l2.ref

    print(f"{'main memory refs':<17}: {mainRef}")
    print(f"{'page table refs':<17}: {pageRef}")
    print(f"{'disk refs':<17}: {diskRef}")


