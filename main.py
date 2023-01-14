import os
import math
import mido

Failed = False

DoALLFiles = True
ListFiles = True

## Volume
maxVolume = 150
minVolume = 15
volumeInterval = 5

midName = 'Midi/test.mid'

Pianodict = {
    36:"1",
    37:"`!",
    38:"2",
    39:"`@",
    40:"3",
    41:"4",
    42:"`$",
    43:"5",
    44:"`%",
    45:"6",
    46:"`^",
    47:"7",
    48:"8",
    49:"`*",
    50:"9",
    51:"`(",
    52:"0",
    53:"q",
    54:"Q",
    55:"w",
    56:"W",
    57:"e",
    58:"E",
    59:"r",
    60:"t",
    61:"T",
    62:"y",
    63:"Y",
    64:"u",
    65:"i",
    66:"I",
    67:"o",
    68:"O",
    69:"p",
    70:"P",
    71:"a",
    72:"s",
    73:"S",
    74:"d",
    75:"D",
    76:"f",
    77:"g",
    78:"G",
    79:"h",
    80:"H",
    81:"j",
    82:"J",
    83:"k",
    84:"l",
    85:"L",
    86:"z",
    87:"Z",
    88:"x",
    89:"c",
    90:"C",
    91:"v",
    92:"V",
    93:"b",
    94:"B",
    95:"n",
    96:"m"
}

if not os.path.exists('Midi/'):
    os.mkdir('Midi/')
    
if not os.path.exists('Output/'):
    os.mkdir('Output/')

Output = '''#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#MaxHotkeysPerInterval 9999
#MaxThreadsPerHotkey 1
SetKeyDelay, -1, -1
Paused := true
F10::ExitApp

Pause::
	Paused := !(Paused)
	Pause, Toggle, 1
	return


#if Paused == true
$Space::Send, {space}
#if Paused == false
Space::Return

#if
F9::
	Paused := false
'''

def GetTrans(notes):
    transposition = 0
    lowest = 100
    highest = 0
    hcount = 0
    lcount = 0
    for n in notes:
        if n > 19 and n < 113:
            if n < lowest:
                lowest = n
            if n > highest:
                highest = n 
            if 36 > n:
                lcount += 1
                if lcount >= hcount:
                    transposition = lowest - 36
            if 96 < n:
                hcount += 1
                if hcount >= lcount:
                    transposition = highest - 96
    return transposition

def GetVolume(velocities,oldVolume):
    returnVar = 100
    sum = 0
    for v in velocities:
        sum += v
    average = sum/len(velocities)
    # print(velocities)
    if average > maxVolume:
        return maxVolume
    elif average < minVolume:
        if average != 0:
            return minVolume
        else:
            return oldVolume
    else:
        # print(average,end="\t")
        if average == 100:
            returnVar = 100
        elif average == 0:
            return oldVolume
        elif average > 100:
            returnVar = average*(127/maxVolume)
        elif average > minVolume:
            returnVar = average
        else:
            # print(average)
            returnVar = minVolume
        # print(returnVar,end="\t")
        # print((returnVar//volumeInterval)*volumeInterval,end="\t")
        # print((returnVar//volumeInterval)*volumeInterval,end = "\tFunction \n")
        return (returnVar//volumeInterval)*volumeInterval
    
def getCmdTable(mid):
    for v in mid:
        if v.type == 'set_tempo':
            tempo = v.tempo
            break

    CmdTable = [[0,[],[],-1,False,[]]] # structured as [sleep time|note on|note off|tempo change if -1 then no change|sustain pedal|Key Velocities]
    # i = 0
    for v in mid:
        if v.type == 'set_tempo':
            tempo = v.tempo
        # i += 1
        # if i < 120:
            # print(v)
            # print(v, f"{round(TotalTime//60)}:{round(TotalTime%60)}")
        if mido.tick2second(v.time, mid.ticks_per_beat, tempo) >= 0:
            time = v.time
        else:
            time = 0

        if ((v.type == 'note_on' or v.type == 'note_off') and (v.note > (19) and v.note < (113))) or v.type == 'set_tempo' or (v.type == 'control_change' and v.control == 64):
            if time != 0:
                CmdTable.append([time,[],[],-1,False,[]])

            if v.type == 'set_tempo':
                tempo = v.tempo
                CmdTable[len(CmdTable)-1][3] = (mido.tempo2bpm(tempo))
            elif v.type == 'note_on':
                if not(v.note in CmdTable[len(CmdTable)-1][1]):
                    CmdTable[len(CmdTable)-1][1].append(v.note)
                    CmdTable[len(CmdTable)-1][5].append(v.velocity)
            elif v.type == 'note_off':
                if not(v.note in CmdTable[len(CmdTable)-1][2]):
                    CmdTable[len(CmdTable)-1][2].append(v.note)
                CmdTable[len(CmdTable)-1][2].append(v.note)
            elif v.type == 'control_change' and v.control == 64:
                CmdTable[len(CmdTable)-1][4] = (True)

        elif v.type == 'note_on' or v.type == 'note_off':
            print("Failed:",v.note)
    return CmdTable
    
# structured as [sleep time|note on|note off|tempo change if -1 then no change|sustain pedal|Note velocity]
def OutputFunc(CmdTable):
    oldVolume = 100
    VolumeStr3 = ""
    oldoldVolumestr = ""
    Commands = ""
    CmdStr = ""
    TotalTime = 0
    for i in range(len(CmdTable)):
        v = CmdTable[i]
        TotalTime += v[0]
        # if TotalTime < 20:
        #     print(v)
        #     print(v, f"\t\t\t{math.floor(TotalTime//60)}:{math.floor(TotalTime%60)}:{math.floor((TotalTime*100)%100)}")
        Commands += f"\n\tSleep, {v[0]*1000}"
        if v[3] != -1:
            Commands += f"\n\t; Tempo: {v[3]}"
        if len(v[1]) > 0 or v[4] == True:
            Commands += "\n"
            if len(v[1]) > 0:
                timecheck = 0
                notefound = False
                timebool = False
                for i2 in range(i, len(CmdTable)):
                    v2 = CmdTable[i2]
                    for note1 in v[1]:
                        if notefound != True:
                            for note2 in v2[2]:
                                if note1 == note2:
                                    notefound = True
                                    break
                        else:
                            break
                    if notefound == True:
                        timecheck += v2[0]
                        if timecheck > 0.5:
                            timebool = True
                        break
                    else:
                        timecheck += v2[0]
                if timebool == True:
                    Commands += f"\n\tSend, {{`\}} "
                Transposition = GetTrans(v[1])
                Volume = GetVolume(v[5],oldVolume)
                # if i < 100: print(v[5],v[1],v[2])
                if oldVolume != Volume:
                    VolumeStr1 = ''
                    if Volume != oldVolume:
                        # print(v)
                        # if i < 50: print(Volume,oldVolume,int((Volume-oldVolume)//volumeInterval),f'{math.floor(TotalTime//60)}:{math.floor(TotalTime%60)}',end="\tList\n")
                        VolumeStr1 = f'\n\tSend, '
                        if Volume > oldVolume:
                            # print(Volume)
                            for _ in range(int((Volume-oldVolume)//volumeInterval)):
                                VolumeStr1 += f'{{Right}}'
                        elif Volume < oldVolume:
                            for _ in range(int((oldVolume-Volume)//volumeInterval)):
                                VolumeStr1 += f'{{Left}}'
                        # VolumeStr3 = oldoldVolumestr
                    # oldoldVolumestr = VolumeStr2
                    oldVolume = Volume
                else:
                    VolumeStr1 = ''
                            
                TranscomStr1 = ""
                TranscomStr2 = ""
                if Transposition != 0:   
                    TranscomStr1 = "\n\tSend, "
                    TranscomStr2 = "\n\tSend, "
                    for i in range(abs(Transposition)):
                        if Transposition < 0:
                            TranscomStr1 += "{down}"
                            TranscomStr2 += "{up}"
                        else:
                            TranscomStr1 += "{up}"
                            TranscomStr2 += "{down}"
                CmdStr = "\n\tSend, "
                for note in v[1]:
                    if note <= (96+Transposition) and note >= (36+Transposition):
                        CmdStr += f"{{{Pianodict[note-Transposition]}}}"
                    else:
                        print("Failed:",note)
                if len(v[1]) != 0:
                    Commands += f"{VolumeStr1}{TranscomStr1}{CmdStr}\t\t\t;{math.floor(TotalTime//60)}:{math.floor(TotalTime%60)} {TranscomStr2}"
                CmdStr = ""
                if timebool == True:
                    Commands += f"\n\tSend, {{`\}} "
                Commands += "\n"
    Commands += oldoldVolumestr
    end = '''\n\tExitApp'''
    worked = False
    while not worked:
        try:
            outputname = ""
            if not DoALLFiles:
                outputname = input("Enter output name: ")
            if outputname == "" or DoALLFiles:
                outputname = "".join(entry.name.split(".")[0:len(entry.name.split("."))-1])
            print(midName)
            with open('Output/'+outputname+'.ahk', 'w') as f:
                f.write(Output+Commands+end)
            worked = True
        except Exception as error:
            print(error)
            worked = False

if not DoALLFiles:
    if ListFiles == True:
        Files = {}
        i = 0
        with os.scandir('./Midi') as dirs:
            for entry in dirs:
                Files.update({i: entry.name})
                i += 1
        for i in range(len(Files)):
            print(i, "\t", Files[i])
        worked = False
        while not worked:
            try:
                filei = int(input("Enter a file number: "))
                midName = 'Midi/'+Files[filei]
                worked = True
            except:
                for i in range(len(Files)):
                    print(i, "\t", Files[i])
        

    mid = mido.MidiFile(midName)
    OutputFunc(getCmdTable(mid))
else:
    with os.scandir('./Midi') as dirs:
        for entry in dirs:
            midName = 'Midi/'+entry.name
            mid = mido.MidiFile(midName)
            OutputFunc(getCmdTable(mid))

if Failed == False:
    print("Done!")
else:
    print("Run again!")