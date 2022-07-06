using {sap.esh.Identifier} from '../../../../model/esh';
namespace example;

type Name: String(256);

entity Person: Identifier {
    firstName: Name;
    lastName: Name;
}