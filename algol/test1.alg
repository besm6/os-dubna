'COMMENT' THE PRIMES FROM 2 TO 100: THE SIEVE OF ERATOSTHENES;
'BEGIN'
    'BOOLEAN' 'ARRAY' PRIME [2:100];
    'INTEGER' N, K;
    'FOR' N:=2 'STEP' 1 'UNTIL' 100 'DO'
        PRIME [N] := 'TRUE';
    'FOR' N:=2 'STEP' 1 'UNTIL' 100 'DO'
        'IF' PRIME[N] 'THEN'
            'FOR' K:=N+N 'STEP' N 'UNTIL' 100 'DO'
                PRIME [K] := 'FALSE';
    'FOR' N:=2 'STEP' 1 'UNTIL' 100 'DO'
        'IF' PRIME[N] 'THEN'
            PRINT (N);
'END'
'EOP'
