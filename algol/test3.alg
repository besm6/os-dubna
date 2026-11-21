'BEGIN'
    'COMMENT' SWITCHES, GOTO, BOOLEANS, WHILE, BLOCKS, ARRAYS, STRINGS;
    'SWITCH' S := L1, L2, L3;
    'INTEGER' I, K; 'BOOLEAN' B, C;
    'ARRAY' A[0:4, -1:1];
    'PROCEDURE' P(N, M); 'VALUE' N; 'INTEGER' N; 'ARRAY' M;
        M[N, 0] := N + 0.5;
    I := 1;
L0: 'GOTO' S[I];
L1: I := I + 1; 'GOTO' L0;
L2: I := I + 1; 'GOTO' L0;
L3: B := I = 3 'AND' 'NOT' (I > 5) 'OR' 'FALSE';
    C := B 'IMPL' 'TRUE' 'EQUIV' 'NOT' B;
    K := 0;
    'FOR' I := 1, 2, 5 'STEP' 2 'UNTIL' 9 'DO' K := K + 1;
    'BEGIN' 'INTEGER' 'ARRAY' X[1:K];
        'FOR' I := 1 'STEP' 1 'UNTIL' K 'DO' X[I] := I * I;
        PRINT(X[K])
    'END';
    'FOR' I := 0 'STEP' 1 'UNTIL' 4 'DO' P(I, A);
    PRINT(A[4, 0], B, C, K);
    PRINT('('HELLO FROM ALGOL')')
'END'
'EOP'
