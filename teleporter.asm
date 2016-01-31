05445: push A
05447: push B
05449: push C
05451:   jf H, 5605  // the Eighth register! - if H = 0 goto 5605
05454: push A
05456: push B
05458: push C
05460:  set A, 28844
05463:  set B, 1531
05466:  add C, 7952, 17624
05470: call 1458  // 'A strange, electronic voice is projected into your mind:
	//  "Unusual setting detected!  Starting confirmation process!  Estimated time to completion: 1 billion years."'
05472:  pop C
05474:  pop B
05476:  pop A
05478: noop 
05479: noop 
05480: noop 
05481: noop 
05482: noop 
05483:  set A, 4
05486:  set B, 1
05489: call 6027 // validation routine
05491:   eq B, A, 6
05495:   jf B, 5579 // if A != 6 goto FAILURE? 

	// SUCCESS(?):-
05498: push A
05500: push B
05502: push C
05504:  set A, 29014
05507:  set B, 1531
05510:  add C, 1415, 4080
05514: call 1458 // 'You wake up on a sandy beach with a slight headache.
	// The last thing you remember is activating that teleporter...
	// but now you can't find it anywhere in your pack.
	// Someone seems to have drawn a message in the sand here:'
05516:  pop C
05518:  pop B
05520:  pop A
05522:  set A, H
05525:  set B, 25866
05528:  set C, 32767
05531: push D
05533:  set D, 29241
05536: call 1841 // generate a code
05538:  pop D
05540: push A
05542: push B
05544: push C
05546:  set A, 29245
05549:  set B, 1531
05552:  add C, 28385, 1938
05556: call 1458 // 'It begins to rain.  The message washes away.
	// You take a deep breath and feel firmly grounded in reality
	// as the effects of the teleportation wear off.'
05558:  pop C
05560:  pop B
05562:  pop A
05564: wmem 2732, 2498 // current location -> beach
05567: wmem 2733, 0
05570:  add B, 2708, 2
05574: wmem B, 32767 // teleporter no longer exists
05577:  jmp 5714

	// FAILURE(?)
05579: push A
05581: push B
05583: push C
05585:  set A, 29400
05588:  set B, 1531
05591:  add C, 461, 536
05595: call 1458 // 'A strange, electronic voice is projected into your mind:
	// "Miscalibration detected!  Aborting teleportation!"
	// Nothing else seems to happen.
05597:  pop C
05599:  pop B
05601:  pop A
05603:  jmp 5714

	// use teleporter without setting eight register to non-zero
05605: push A
05607: push B
05609: push C
05611:  set A, 29545
05614:  set B, 1531
05617:  add C, 572, 14889
05621: call 1458 // 'You activate the teleporter!  As you spiral
	// through time and space, you think you see a pattern in the stars...
05623:  pop C
05625:  pop B
05627:  pop A
05629:  set A, 0        // A = 0
05632:  add C, 1, 27101 // C = 27101+1
	
05636: rmem B, C        // B = memory[C]
05639:  add A, A, B     // A = A + B
05643: mult A, A, 31660 // A = A * 31660
05647: call 2125        // A = A ^ B
05649: rmem B, 27101    // B = memory[27101]
05652:  add B, B, 27101 // B = B + 27101
05656:  add C, C, 1     // C = C + 1
05660:   gt B, C, B     // 
05664:   jf B, 5636     // if C <= B goto 5636
05667:  set B, 25866
05670:  set C, 32767
05673: push D
05675:  set D, 29663
05678: call 1841 // generate code 6
05680:  pop D
05682: push A
05684: push B
05686: push C
05688:  set A, 29667
05691:  set B, 1531
05694:  add C, 11933, 2914
05698: call 1458 // 'After a few moments, you find yourself back on
	// solid ground and a little disoriented.'
05700:  pop C
05702:  pop B
05704:  pop A
05706: wmem 2732, 2488 // current location -> synacor HQ
05709: wmem 2733, 0
05712:  jmp 5714 // STRANGE!
05714:  pop C
05716:  pop B
05718:  pop A
05720:  ret 

	// subr(s) for validation
	
06027:   jt A, 6035     // if A != 0 goto 6035
06030:  add A, B, 1     // A = B + 1
06034:  ret
	
06035:   jt B, 6048     // if B != 0 goto 6048
06038:  add A, A, 32767 // A = A + 32767 = A - 1
06042:  set B, H        // B = H
06045: call 6027        // call 6027
06047:  ret
	
06048: push A		// push A
06050:  add B, B, 32767 // B = B + 32767 = B - 1
06054: call 6027	// call 6027
06056:  set B, A        // B = A
06059:  pop A           // pop A
06061:  add A, A, 32767 // A = A + 32767 = A - 1
06065: call 6027        // call 6027
06067:  ret             // ret
