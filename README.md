# freeElmo

MultiOS Client for Elmo Document Camera

(currently is everything based on the L-12, predecessor of the TT-12)

## Communication between ImageMate and Elmo

1. Version
2. Sync1
3. Sync2
4. Sync3
5. Picture
6. Version
7. Picture
8. Version
usw.

We have absolutly no idea what are the values which  are returned in 2-4. 
But, these 3 values (004, 191, 060) don't seem to be important.


## Command-Glossary

### Version

:IN:  01:00:81                                                                  
:OUT: 01:00:02

    0000 0000 1800 0000 108B 0000 0000 0000 
    0000 0000 0000 0000 0000 0000 0000 0000

**possible answer:**

    0100 0000 1800 0000 0000 0000 4C2D 3132  ............L-12
    0000 0000 0000 0000 0000 0000 0000 0000  ................

### Sync1

**IN** | 01:00:81                                                                  
**OUT**| 01:00:02

    0000 0000 1800 0000 118B 0000 0000 0000
    0000 0000 0000 0000 0000 0000 0000 0000

**possible answer:**

    0100 0000 1800 0000 0000 0000 5741 2E31  ............WA.1
    2E30 3034 0000 0000 0000 0000 0000 0000  .004............

### Sync2

**IN** | 01:00:81                                                                  
**OUT**| 01:00:02

    0000 0000 1800 0000 118B 0000 0100 0000                                       
    0000 0000 0000 0000 0000 0000 0000 0000

**possible answer:**

    0100 0000 1800 0000 0000 0000 5741 2E31  ............WA.1                     
    2E31 3931 0000 0000 0000 0000 0000 0000  .191............

### Sync3

**IN** | 01:00:81                                                                  
**OUT**| 01:00:02

    0000 0000 1800 0000 118B 0000 0200 0000                                       
    0000 0000 0000 0000 0000 0000 0000 0000                                       
                                                                                
**possible answer**                                                                

    0100 0000 1800 0000 0000 0000 5741 2E31  ............WA.1
    2E30 3630 0000 0000 0000 0000 0000 0000  .060............

### Picture

**IN** | 01:00:83                                                                  
**OUT**| 01:00:04

    0000 0000 1800 0000 8E80 0000 5000 0000 
    0000 0000 0000 0000 0000 0000 0000 0000

**possible answer**

    0000 0000 1800 0000 XXXX 0000 5000 0000 
    0000 0000 0000 0000 0000 0000 0000 0000 
    0200 0000 F8FE 0000 PPPPPPPPPPPPPPPPPPP
    PPPP ....
    0200 0000 F8FE 0000 PPPPPPPPPPPPPPPPPPP
    PPPP ....
* X stands for size of picture without header
* P is picture data as bytestream splitted in 65272 bytes and header
