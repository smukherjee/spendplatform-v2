import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './screens/Dashboard';
import Login from './screens/Login';
import Invoices from './screens/Invoices';
import InvoiceDetail from './screens/InvoiceDetail';
import InvoiceEdit from './screens/InvoiceEdit';
import Suppliers from './screens/Suppliers';
import SupplierDetail from './screens/SupplierDetail';
import SupplierEdit from './screens/SupplierEdit';
import BusinessUnits from './screens/BusinessUnits';
import BusinessUnitDetail from './screens/BusinessUnitDetail';
import BusinessUnitEdit from './screens/BusinessUnitEdit';
import Regions from './screens/Regions';
import RegionDetail from './screens/RegionDetail';
import RegionEdit from './screens/RegionEdit';
import Roles from './screens/Roles';
import RoleDetail from './screens/RoleDetail';
import RoleEdit from './screens/RoleEdit';
import Users from './screens/Users';
import UserDetail from './screens/UserDetail';
import UserEdit from './screens/UserEdit';
import Clients from './screens/Clients';
import ClientDetail from './screens/ClientDetail';
import ClientEdit from './screens/ClientEdit';
import Subcategories from './screens/Subcategories';
import SubcategoryDetail from './screens/SubcategoryDetail';
import SubcategoryEdit from './screens/SubcategoryEdit';
import UnitOfMeasure from './screens/UnitOfMeasure';
import UnitOfMeasureDetail from './screens/UnitOfMeasureDetail';
import UnitOfMeasureEdit from './screens/UnitOfMeasureEdit';
import Currency from './screens/Currency';
import CurrencyDetail from './screens/CurrencyDetail';
import CurrencyEdit from './screens/CurrencyEdit';
import ImportErrors from './screens/ImportErrors';
import Reporting from './screens/Reporting';
import ClientSettings from './screens/ClientSettings';
import Settings from './screens/Settings';

export default function AppRoutes() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/invoices" element={<Invoices />} />
        <Route path="/invoices/:id" element={<InvoiceDetail />} />
        <Route path="/invoices/:id/edit" element={<InvoiceEdit />} />
        <Route path="/suppliers" element={<Suppliers />} />
        <Route path="/suppliers/:id" element={<SupplierDetail />} />
        <Route path="/suppliers/:id/edit" element={<SupplierEdit />} />
        <Route path="/business-units" element={<BusinessUnits />} />
        <Route path="/business-units/:id" element={<BusinessUnitDetail />} />
        <Route path="/business-units/:id/edit" element={<BusinessUnitEdit />} />
        <Route path="/regions" element={<Regions />} />
        <Route path="/regions/:id" element={<RegionDetail />} />
        <Route path="/regions/:id/edit" element={<RegionEdit />} />
        <Route path="/roles" element={<Roles />} />
        <Route path="/roles/:id" element={<RoleDetail />} />
        <Route path="/roles/:id/edit" element={<RoleEdit />} />
        <Route path="/users" element={<Users />} />
        <Route path="/users/:id" element={<UserDetail />} />
        <Route path="/users/:id/edit" element={<UserEdit />} />
        <Route path="/clients" element={<Clients />} />
        <Route path="/clients/:id" element={<ClientDetail />} />
        <Route path="/clients/:id/edit" element={<ClientEdit />} />
        <Route path="/subcategories" element={<Subcategories />} />
        <Route path="/subcategories/:id" element={<SubcategoryDetail />} />
        <Route path="/subcategories/:id/edit" element={<SubcategoryEdit />} />
        <Route path="/unit-of-measure" element={<UnitOfMeasure />} />
        <Route path="/unit-of-measure/:id" element={<UnitOfMeasureDetail />} />
        <Route path="/unit-of-measure/:id/edit" element={<UnitOfMeasureEdit />} />
        <Route path="/currency" element={<Currency />} />
        <Route path="/currency/:id" element={<CurrencyDetail />} />
        <Route path="/currency/:id/edit" element={<CurrencyEdit />} />
        <Route path="/import-errors" element={<ImportErrors />} />
        <Route path="/reporting" element={<Reporting />} />
        <Route path="/client-settings" element={<ClientSettings />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Router>
  );
}
