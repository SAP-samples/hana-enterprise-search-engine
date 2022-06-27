namespace example;

entity L0 {
    pl0             : many {
        pl1         : many {
            pl2     : many {
                pl3 : String(80);
            };
        };
    };
}
