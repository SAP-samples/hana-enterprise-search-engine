namespace example;

type Code : String(80);

aspect Base {
    description : String(120)
};

aspect Relationship {}
entity Codelist : Base {};
entity CodelistRelV : Codelist {};
entity CodelistRelFP : Codelist {};
entity CodelistRelPA : Codelist {};
entity CodelistRelPN : Codelist {};
entity CodelistRelWP : Codelist {};
entity CodelistRelFW : Codelist {};

entity V : Base {
    relF : Association to many RelVF;
    relW : Association to many RelVW;
    relA : Association to many RelVA;
    relP : Association to many RelVP;
};

entity F : Base {
    relP : Association to many RelFP;
    relW : Association to many RelFW;
    relV : Association to RelVF;
};

entity W : Base {
    relP : Association to many RelWP;
    relV : Association to RelVW;
    relF : Association to many RelFW;
};

entity A : Base {
    relV : Association to RelVA;
    relP : Association to many RelPA;
};

entity P : Base {
    relA : Association to many RelPA;
    relN : Association to RelPN;
    relV : Association to RelVP;
    relF : Association to many RelFP;
};

entity N : Base {
    relP : Association to many RelPN;
};

entity RelVF : Relationship {
    v : Association to V;
    f : Association to F;
    type: Association to CodelistRelV;
};

entity RelVW : Relationship {
    v : Association to V;
    w : Association to W;
    type: Association to CodelistRelV;
}

entity RelVP : Relationship {
    v : Association to V;
    p : Association to P;
    type: Association to CodelistRelV;
};

entity RelVA : Relationship {
    v : Association to V;
    a : Association to A;
    type: Association to CodelistRelV;
};

entity RelFP {
    f : Association to F;
    p : Association to P;
    type: Association to CodelistRelFP;
};

entity RelWP : Relationship {
    w : Association to W;
    p : Association to P;
    type: Association to CodelistRelWP;
};

entity RelPA : Relationship {
    p : Association to P;
    a : Association to A;
    type: Association to CodelistRelPA;
};

entity RelFW : Relationship {
    f : Association to F;
    w : Association to W;
    type: Association to CodelistRelFW;
};

entity RelPN : Relationship {
    p : Association to P;
    n : Association to N;
    type: Association to CodelistRelPN;
};
