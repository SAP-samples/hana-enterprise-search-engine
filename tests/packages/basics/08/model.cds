namespace example;

entity L0 {
    pl0: many L1;
}

type L1 {
    pl1: many L2;
}

type L2 {
    pl2: many L3;
}

type L3 {
    pl3: String(80);
};