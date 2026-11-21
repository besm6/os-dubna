'BEGIN'
    'COMMENT' PROCEDURES, REALS, RECURSION, NAME AND VALUE PARAMETERS;
    'REAL' 'PROCEDURE' F(X); 'VALUE' X; 'REAL' X;
        F := 'IF' X < 1.0 'THEN' 1.0 'ELSE' X * F(X - 1.0);
    'INTEGER' 'PROCEDURE' SUM(I, A, B, T); 'VALUE' A, B;
        'INTEGER' I, A, B, T;
    'BEGIN' 'INTEGER' S; S := 0;
        'FOR' I := A 'STEP' 1 'UNTIL' B 'DO' S := S + T;
        SUM := S
    'END';
    'PROCEDURE' SWAP(P, Q); 'REAL' P, Q;
    'BEGIN' 'REAL' T; T := P; P := Q; Q := T 'END';
    'INTEGER' J; 'REAL' U, V;
    'INTEGER' 'ARRAY' C[1:3];
    U := 1.5; V := -0.00225;
    SWAP(U, V);
    PRINT(U, V, F(5.0), SUM(J, 1, 10, J*J));
    PRINT(SQRT(2.0), SIN(1.0), COS(1.0));
    PRINT(ARCTAN(1.0), LN(10.0), EXP(1.0));
    PRINT(ABS(-3), SIGN(-2.0), ENTIER(3.7));
    C[2] := ENTIER(7 / 2); PRINT(C[2], 7 / 2)
'END'
'EOP'
