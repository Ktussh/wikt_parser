
# coding: utf-8

# In[66]:


#--encoding utf-8
import codecs
import bz2


def page_parser(in_file, out_file):
    
    title = -1
    ns = -1
    meaning = []
    example = []
    synonym = []
    
    while True:
        
        line = in_file.readline()
        
        if "</page>" in line:
            return False
            
        if "<title>" in line:
            rus_flag, title = title_parser(line)
            if rus_flag == False:
                return rus_flag
            continue
        
        if "<ns>" in line:
            if not "<ns>0</ns>" in line:
                return False
            ns = 0
            continue
            
        if "<redirect>" in line:
            return False
        
        if "<text" in line:
            if title == -1:
                return False
            if ns == -1:
                return False
            rus_flag, meaning, synonym = text_parser(line, in_file)
            if rus_flag == False:
                return rus_flag
            break
    
    if title == -1:
        return False
    if ns == -1:
        return False
        
    out_file.write("<word>\n<title>"+title+"</title>\n")
    tmp_ex = []
    for i in xrange(len(meaning)):
        meaning[i], tmp_ex = meaning_parser(meaning[i])
        out_file.write("<mean"+str(i)+">\n<meaning>"+meaning[i]+"</meaning>\n")
        out_file.write("<examples>\n")
        for j in xrange(len(tmp_ex)):
            tmp_ex[j] = example_parser(tmp_ex[j])
            out_file.write("<example"+str(j)+">"+tmp_ex[j]+"</example"+str(j)+">\n")
        out_file.write("</examples>\n<synonyms>\n")
        if i >= len(synonym):
            out_file.write("</synonyms>\n</mean"+str(i)+">\n")
            continue
        synonym[i] = synonym_parser(synonym[i])
        list_of_synonyms = synonym[i].split(',')
        for j in xrange(len(list_of_synonyms)):
            list_of_synonyms[j] = list_of_synonyms[j].strip()
            out_file.write("<synonym"+str(j)+">"+list_of_synonyms[j]+"</synonym"+str(j)+">\n")
        out_file.write("</synonyms>\n</mean"+str(i)+">\n")
    out_file.write("</word>\n")
    return True

def title_parser(titl):
    
    titl = titl.decode('utf-8')
    titl = titl.replace("<title>","")
    titl = titl.replace("</title>","")
    titl = titl.strip()
    
    flag = True
    for l in titl:
        if (l < u'а' or l > u'я') and (l < u'А' or l > u'Я') and l != u'ё' and l != u'Ё':
            flag = False
            break
    return flag, titl

def text_parser(line, in_file):
    
    flag = False
    meaning = []
    synonym = []
    n = 0
    
    while not "</text>" in line:
            
        if "= {{-ru-}} =" in line:
            flag = True
            line = in_file.readline()
            continue
        if flag == False:
            line = in_file.readline()
            continue
                
        if not(u"==== Значение ====" in line.decode('utf-8')) and not (u"==== Синонимы ====" in line.decode('utf-8')):
            line = in_file.readline()
            continue
                
        if u"==== Значение ====" in line.decode('utf-8'):
            line = in_file.readline()
            while "#" in line:
                line = line.strip()
                line = line.replace("#","")
                if line != "":
                    n += 1
                    meaning += [line]
                line = in_file.readline()
                
        if u"==== Синонимы ====" in line.decode('utf-8'):
            line = in_file.readline()
            if "</text>" in line:
                continue
            while "#" in line:
                line = line.strip()
                line = line.replace("#","")
                synonym += [line]
                line = in_file.readline()
            synonym = synonym[:n]
            line = "</text>"
                
    return flag, meaning, synonym
    
def russian_symbols(param):
    par = ""
    for c in param:
        if c == '|':
            par += ' '
            continue
        if (c >= u'а' and c <= u'я') or (c >= u'А' and c <= u'Я') or c == u'ё' or c == u'Ё':
            par +=c
            continue
        if c == '.' or c == ',' or c == ';' or c == ':' or c == ' ':
            par +=c
            continue
        if c == '!' or c == '?' or c == '-' or c == "%" or c == '/':
            par +=c
            continue
        if c >='0' and c <= '9' or c == '(' or c == ')':
            par +=c
            continue
    return par

def del_marks(param):
    
    if not ";!--" in param:
        return param
    
    par = ""
    i = 0
    while i < len(param):
        if i+3 < len(param) and param[i] == ";" and param[i+1] == "!" and param[i+2] == "-" and param[i+3] == "-": 
            i += 4
            while i+2 < len(param) and (param[i] != "-" or param[i+1] != "-" or param[i+2] != ";"):
                i +=1
            continue
            #j = 1
            #if i+j < len(param) and param[i+j] != "!":
            #    i += 1
            #    continue
            #j+=1
            #if i+j < len(param) and param[i+j] != "-":
            #    i += 1
            #    continue
            #j+=1
            #if i+j < len(param) and param[i+j] != "-":
            #    i += 1
            #    continue
            #j+=1
            #while i+j+1 < len(param) and param[i+j] != ";":
            #    j += 1
            #if i+j >= len(param):
            #    continue
            #if param[i+j] != ";":
            #    i += 1
            #    continue
            #i += j+1
            #continue
        par += param[i]
        i += 1
    return par
    
def meaning_parser (mean):
    
    mean = mean.decode('utf-8')
    ex = []
    i = 0
    me = ""
    
    ex = mean.split(u"{пример")
    mean = ex[0]
    ex = ex[1:]
    
    while i < len(mean):
        if mean[i]=="{":
            j = 0
            while i+j+1 != len(mean) and mean[i+j] != "|" and mean[i+j] != "}":
                j += 1
            if mean[i+j] == '|':
                i += j
                continue
            i += 1
            continue
        if mean[i]=="[":
            j = 0
            while i+j+1 != len(mean) and mean[i+j] != "|" and mean[i+j] != "]":
                j += 1
            if mean[i+j] == '|':
                i += j
                continue
            i += 1
            continue
        me+=mean[i]
        i +=1
        
    me = russian_symbols(me)
    me = del_marks(me)
    while me != me.replace("  "," "):
        me = me.replace("  "," ")
    me = me.strip()
    if len(me) == 0:
        return me, ex
    if me[0] == ',':
        me  = me[1:]
    me = me.replace("()","")
    me = me.strip()
    me = me.replace("..",".")
    
    return me, ex

def synonym_parser (syn):
    
    syn = syn.decode('utf-8')
    sy = ""
    i = 0
    
    if len(syn) != 0 and syn[i] == '|':
        i+=1
    while i < len(syn):
        if syn[i]=="{":
            j = 0
            while i+j+1 != len(syn) and syn[i+j] != "}":
                j += 1
            if syn[i+j] == '}':
                i += j
                while i != len(syn) and syn[i] == '}':
                    i += 1
                continue
            while i != len(syn) and syn[i] == '{':
                i += 1
        if syn[i]=='[':
            j = 1
            while i+j != len(syn) and syn[i+j] != '|' and syn[i+j] != ']':
                j += 1
            if syn[i+j] == '|':
                i += j+1
                continue
            i += 1
            continue
        if syn[i] == ']':
            i += 1
            continue
        sy+=syn[i]
        i +=1
    
    sy = russian_symbols(sy)
    sy = del_marks(sy)
    while sy != sy.replace("  "," "):
        sy = sy.replace("  "," ")
    sy = sy.strip()
    if len(sy) == 0:
        return sy
    if sy[0] == ',':
        sy = sy[1:]
    sy = sy.replace("()","")
    sy = sy.strip()
    sy = sy.replace("..",".")
    return sy

def example_parser(exam):
    ex = ""
    i = 0
    if len(exam) == 0:
        return exam
    if exam[i] == '|':
        i += 1
    while i < len(exam):
        if exam[i] == '|':
            break
        if exam[i] == '{':
            while exam[i] != '|'and i+1 != len(exam) and exam[i+1] != '}':
                i += 1
            i += 1
            while i != len(exam) and exam[i] != '}':
                ex += exam[i]
                i += 1
            i += 2
            continue
        if exam[i] == '}':
            break
        ex += exam[i]
        i += 1
        
    ex = russian_symbols(ex)
    ex = del_marks(ex)
    while ex != ex.replace("  "," "):
        ex = ex.replace("  "," ")
    ex = ex.replace("()","")
    ex = ex.strip()
    ex = ex.replace("..",".")
    return ex

        
#.............Main................
input_file_name = "wikt.xml.bz2"
output_file_name = "wiki_parsed.xml"
bz_file = bz2.BZ2File(input_file_name)
file_new = codecs.open(output_file_name, mode="w", encoding="utf-8")
line = ""
count = 0
while True:
    
    line = bz_file.readline()
    if line == "":
        break
        
        
    if "<page>" in line:
        page_parser(bz_file, file_new)

file_new.close()

