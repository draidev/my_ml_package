import os
import pefile
import struct
import datetime
import hashlib
from collections import defaultdict

class PE_HEADER:
    def __init__(self, file_path=None):
        self.pe = None
        if file_path != None:
            self.file_path = file_path

            try:
                self.pe = pefile.PE(file_path)
            except FileNotFoundError:
                print(f"File not found: {file_path}")
            except pefile.PEFormatError as e:
                print(f"PEFormatError: {file_path} does not appear to ba a PE file.")
                print("Error:", e)
                return
         

    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_pe(self, pe):
        self.pe = pe

    def print_info (self, data_list) :
        for data in data_list :
            print(data[0].ljust(20), str(data[1]).ljust(20), data[2].ljust(20))

    def nt_header_info (self) :
        print("-" * 30)
        print("[NT header]에서 필요한 정보\n")
        nt_header_list = []
        nt_header_list.append(["실제 변수명", "값", "의미"])
        nt_header_list.append(["Signature", struct.pack('<I', self.pe.NT_HEADERS.Signature).decode('utf8'), "NF Signature"])
        nt_header_list.append(["Machine", hex(self.pe.FILE_HEADER.Machine), "CPU 별 고유값 (x86 = 0x14c / x64 = 0x8664)"])
        
        timeStr = '1970-01-01 00:00:00'
        Thistime = datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S') 
        LastBuildtime = Thistime + datetime.timedelta(seconds=self.pe.FILE_HEADER.TimeDateStamp)

        nt_header_list.append(["TimeDateStamp", str(LastBuildtime), "파일을 빌드한 시간"])
        nt_header_list.append(["NumberOfSections", self.pe.FILE_HEADER.NumberOfSections, "Section의 총 개수"])
        nt_header_list.append(["SizeOfOptionalHeader", hex(self.pe.FILE_HEADER.SizeOfOptionalHeader), "OptionalHeader의 크기"])
        nt_header_list.append(["Characteristics", hex(self.pe.FILE_HEADER.Characteristics), "이 파일의 속성"])
        nt_header_list.append(["Magic", hex(self.pe.OPTIONAL_HEADER.Magic), "Optional header를 구분하는 Signature (32bit=10b / 64bit=20b)"])
        nt_header_list.append(["SizeOfCode", hex(self.pe.OPTIONAL_HEADER.SizeOfCode), "IMAGE_SCN_CNT_CODE 속성을 갖는 섹션들의 총 사이즈 크기"])
        nt_header_list.append(["AddressOfEntryPoint", hex(self.pe.OPTIONAL_HEADER.AddressOfEntryPoint), "PE 파일이 메모리 로드 후 처음 실행되어야 하는 코드 주소"])
        nt_header_list.append(["ImageBase",  hex(self.pe.OPTIONAL_HEADER.ImageBase), "PE파일이 매핑되는 시작주소"])
        nt_header_list.append(["SectionAlignment", self.pe.OPTIONAL_HEADER.SectionAlignment, "메모리 상에서의 최소 섹션 단위"])
        nt_header_list.append(["FileAlignment", self.pe.OPTIONAL_HEADER.FileAlignment, "파일 상에서의 최소 섹션 단위"])
        
        self.print_info (nt_header_list)
        
        print("-" * 30,"\n")   

    def get_TimeDateStamp(self):
        timeStr = '1970-01-01 00:00:00'
        Thistime = datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S') 
        LastBuildtime = Thistime + datetime.timedelta(seconds=self.pe.FILE_HEADER.TimeDateStamp)

        return str(LastBuildtime)


    def sections_header_info (self) :
        print("-" * 30)
        print("[sections_info]에서 필요한 정보\n")
        print("\t개념")
        print("Name".ljust(20), "Section 이름을 나타냄")
        print("VirtualAddress".ljust(20), "섹션의 RAV(ImageBase + VA)를 위한 VA 값")
        print("SizeOfRawData".ljust(20), "파일 상에서 섹션이 차지하는 크기")
        print("PointerToRawData".ljust(20), "파일 상에서 섹션이 시작하는 위치")
        print("Characteristics".ljust(20), "섹션의 특징을 나타냄")
        print("".ljust(20), "(0x20000000 = excutable, 0x40000000 = readable, 0x80000000 = writeable, 0x00000020 = contains code, 0x00000040 = contains initialized data)")
        print("")
        
        print("Name".ljust(20), "Virtual Address".ljust(20), "SizeOfRawData".ljust(20),
              "PointerToRawData".ljust(20), "Characteristics".ljust(20))
        for section in self.pe.sections :     
             print(section.Name.decode('utf8').ljust(20), hex(section.VirtualAddress).ljust(20),
                   hex(section.SizeOfRawData).ljust(20), hex(section.PointerToRawData).ljust(20), hex(section.Characteristics))      
             
        print("-" * 30,"\n")


    def get_imported_dll_function(self):
        if not os.path.isfile(self.file_path):
            print(f"The file {self.file_path} does not exist.")
            return
        
        try:
            pe = pefile.PE(self.file_path)
        except pefile.PEFormatError:
            print(f"The file {self.file_path} does not appear to be a valid PE file.")
            return
        
        print(f"Analyzing: {self.file_path}\n")
        
        imported_dll_dict = defaultdict(list)
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
                cur_dll = entry.dll.decode('utf-8')
                imported_dll_dict[cur_dll]
                print(f"Imported DLL: {cur_dll}")
                for imp in entry.imports:
                    if imp.name:
                        cur_imp = imp.name.decode('utf-8')
                        imported_dll_dict[cur_dll].append(cur_imp)
                        print(f"\tImported function: {cur_imp}")
                    else:
                        print(f"\tImported function by ordinal: {imp.ordinal}")
                print("\n")
        else:
            print("No imported functions found.")

        return imported_dll_dict
 
