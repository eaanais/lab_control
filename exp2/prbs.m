
T = 1;
Range = [0,1];
Band = [0 1/T];
N = 6;
M=3;
muestras = [2^N-1,1,M];
%[100,1,3]
u = idinput(muestras,'prbs',Band,Range);

u = iddata([],u,1);
plot(u);
title('Periodic Signal')