using {sap.esh.Identifier} from '../../../../model/esh';
namespace example;

entity Person: Identifier {
    firstName: String(256);
    lastName: String(256);
}