from enum import Enum

class MCUButton(Enum):
  REC1         = 0
  REC2         = 1
  REC3         = 2
  REC4         = 3
  REC5         = 4
  REC6         = 5
  REC7         = 6
  REC8         = 7
  SOLO1        = 8
  SOLO2        = 9
  SOLO3        = 10
  SOLO4        = 11
  SOLO5        = 12
  SOLO6        = 13
  SOLO7        = 14
  SOLO8        = 15
  MUTE1        = 16
  MUTE2        = 17
  MUTE3        = 18
  MUTE4        = 19
  MUTE5        = 20
  MUTE6        = 21
  MUTE7        = 22
  MUTE8        = 23
  SELECT1      = 24
  SELECT2      = 25
  SELECT3      = 26
  SELECT4      = 27
  SELECT5      = 28
  SELECT6      = 29
  SELECT7      = 30
  SELECT8      = 31
  VSELECT1     = 32
  VSELECT2     = 33
  VSELECT3     = 34
  VSELECT4     = 35
  VSELECT5     = 36
  VSELECT6     = 37
  VSELECT7     = 38
  VSELECT8     = 39
  TRACK        = 40
  SEND         = 41
  PAN          = 42
  PLUGIN       = 43
  EQ           = 44
  INSTRUMENT   = 45
  BANKLEFT     = 46
  BANKRIGHT    = 47
  CHANNELLEFT  = 48
  CHANNELRIGHT = 49
  FLIP         = 50
  GLOBALVIEW   = 51
  NAME         = 52
  SMPTE        = 53
  F1           = 54
  F2           = 55
  F3           = 56
  F4           = 57
  F5           = 58
  F6           = 59
  F7           = 60
  F8           = 61
  MIDITRACKS   = 62
  INPUTS       = 63
  AUDIOTRACKS  = 64
  AUDIOINSTRUMENT = 65
  AUX          = 66
  BUSSES       = 67
  OUTPUTS      = 68
  USER         = 69
  SHIFT        = 70
  OPTION       = 71
  CONTROL      = 72
  CMD          = 73
  READ         = 74
  WRITE        = 75
  TRIM         = 76
  TOUCH        = 77
  LATCH        = 78
  GROUP        = 79
  SAVE         = 80
  UNDO         = 81
  CANCEL       = 82
  ENTER        = 83
  MARKER       = 84
  NUDGE        = 85
  CYCLE        = 86
  DROP         = 87
  REPLACE      = 88
  CLICK        = 89
  SOLO         = 90
  REWIND       = 91
  FASTFWD      = 92
  STOP         = 93
  PLAY         = 94
  RECORD       = 95
  CURSORUP     = 96
  CURSORDOWN   = 97
  CURSORLEFT   = 98
  CURSORRIGHT  = 99
  ZOOM         = 100
  SCRUB        = 101
  USERSWITCHA  = 102
  USERSWITCHB  = 103
  FADERTOUCH1  = 104
  FADERTOUCH2  = 105
  FADERTOUCH3  = 106
  FADERTOUCH4  = 107
  FADERTOUCH5  = 108
  FADERTOUCH6  = 109
  FADERTOUCH7  = 110
  FADERTOUCH8  = 111
  FADERTOUCHMASTER = 112
  SMTPELED     = 113
  BEATSLED     = 114
  RUDESOLOLIGHT = 115
  RELAYCLICK   = 118

class MCUVPot(Enum):
  SINGLE = 0
  BOOSTCUT = 1
  WRAP = 2
  SPREAD = 3