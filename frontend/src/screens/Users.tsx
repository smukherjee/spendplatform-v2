import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { DataTable, DataTableFilterMeta } from 'primereact/datatable';
import { Column, ColumnEditorOptions } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { MultiSelect } from 'primereact/multiselect';
import { Password } from 'primereact/password';
import { Toast } from 'primereact/toast';
import { Toolbar } from 'primereact/toolbar';
import { confirmDialog, ConfirmDialog } from 'primereact/confirmdialog';
import { FilterMatchMode } from 'primereact/api';
import { fetchUsers, createUser, updateUser, deleteUser, fetchClients, fetchRoles, resetUserPassword, Client, Role, createTestToken } from '../services/api';
import { useMobileDetection } from '../hooks/useMobileDetection';
import { UserTableErrorBoundary } from '../components/UserTableErrorBoundary';
import { 
  createDebouncer, 
  getMemoryUsage 
} from '../utils/userTableUtils';
import 'primereact/resources/themes/lara-light-cyan/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import './Users.css';

export interface User {
  id: string | number;
  name: string;
  username?: string;
  email: string;
  client_id?: number;
  client_name?: string;
  roles?: string[];
  personalisation?: any;
  password?: string; // For new user creation only
}

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [lazyLoading, setLazyLoading] = useState(false);
  const [userDialog, setUserDialog] = useState(false);
  const [user, setUser] = useState<User>({} as User);
  const [selectedUsers, setSelectedUsers] = useState<User[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [globalFilter, setGlobalFilter] = useState('');
  const [filters, setFilters] = useState<DataTableFilterMeta>({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    name: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    email: { value: null, matchMode: FilterMatchMode.CONTAINS },
    client_name: { value: null, matchMode: FilterMatchMode.CONTAINS },
    roles: { value: null, matchMode: FilterMatchMode.CONTAINS }
  });
  const [lastFetchTime, setLastFetchTime] = useState<number>(0);
  const [clients, setClients] = useState<Client[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loadingClients, setLoadingClients] = useState(false);
  const [loadingRoles, setLoadingRoles] = useState(false);
  const [passwordResetDialog, setPasswordResetDialog] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [selectedUserForReset, setSelectedUserForReset] = useState<User>({} as User);
  
  // Performance utilities
  const debouncedSearch = useMemo(() => createDebouncer((term: string) => {
    // Debounced search implementation can be added here if needed
  }, 300), []);
  const [editingRows, setEditingRows] = useState({});
  const [totalRecords, setTotalRecords] = useState(0);
  const [lazyState, setLazyState] = useState({
    first: 0,
    rows: 10,
    page: 1,
    sortField: '',
    sortOrder: 1,
    filters: {}
  });
  const [isAddingNew, setIsAddingNew] = useState(false);
  const toast = useRef<Toast>(null);
  const dt = useRef<DataTable<User[]>>(null);
  
  // Use custom mobile detection hook
  const { isMobile, isTablet, screenSize, touchDevice, deviceInfo } = useMobileDetection();

  // Load clients function
  const loadClients = useCallback(async () => {
    if (loadingClients) return;
    
    try {
      setLoadingClients(true);
      console.log('🏢 Loading clients...');
      const clientData = await fetchClients();
      console.log('✅ Clients loaded:', clientData);
      setClients(clientData);
    } catch (error) {
      console.error('🚫 Failed to load clients:', error);
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Load Error', 
        detail: 'Failed to load clients', 
        life: 3000 
      });
    } finally {
      setLoadingClients(false);
    }
  }, [loadingClients]);

  // Load roles function
  const loadRoles = useCallback(async () => {
    if (loadingRoles) return;
    
    try {
      setLoadingRoles(true);
      console.log('👑 Loading roles...');
      const roleData = await fetchRoles();
      console.log('✅ Roles loaded:', roleData);
      setRoles(roleData);
    } catch (error) {
      console.error('🚫 Failed to load roles:', error);
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Load Error', 
        detail: 'Failed to load roles', 
        life: 3000 
      });
    } finally {
      setLoadingRoles(false);
    }
  }, [loadingRoles]);

  // Debounced search for performance
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      // Global filter is already handled by the input onChange
    }, 300); // 300ms debounce

    return () => clearTimeout(debounceTimer);
  }, [globalFilter]);

  // Log device info for debugging (remove in production)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('Device Detection:', {
        isMobile,
        isTablet,
        screenSize,
        touchDevice,
        userAgent: deviceInfo.userAgent.substring(0, 50) + '...'
      });
    }
  }, [isMobile, isTablet, screenSize, touchDevice, deviceInfo]);

  const loadUsers = useCallback(async (lazyParams?: any, force = false) => {
    // Prevent multiple concurrent calls
    if (loading && !force) {
      console.log('⏭️ Skipping load - already loading');
      return;
    }
    
    try {
      console.log('🔄 Loading users...', { force, usersLength: users.length, lastFetchTime });
      
      // Skip if data is fresh and not forced (but allow initial load)
      const now = Date.now();
      const CACHE_DURATION = 2 * 60 * 1000; // 2 minutes for user data
      
      if (!force && users.length > 0 && lastFetchTime > 0 && (now - lastFetchTime) < CACHE_DURATION) {
        console.log('⏭️ Skipping load - data is fresh');
        return;
      }

      setLoading(true);
      console.log('🔄 Setting loading state...');
      
      const startTime = performance.now();
      
      // Fetch data from database only
      console.log('📡 Fetching users from database...');
      
      const data = await fetchUsers();
      console.log('✅ API Response received:', data);
      
      if (!data) {
        console.warn('� No data received from API');
        setUsers([]);
        setTotalRecords(0);
        toast.current?.show({ 
          severity: 'warn', 
          summary: 'No Data', 
          detail: 'No users found in the database', 
          life: 3000 
        });
        return;
      }
      
      if (!Array.isArray(data)) {
        console.error('� API returned non-array data:', typeof data, data);
        setUsers([]);
        setTotalRecords(0);
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Data Error', 
          detail: 'Invalid data format received from server', 
          life: 5000 
        });
        return;
      }
      
      console.log('� Setting API data:', data.length, 'users');
      console.log('🔍 Raw API data:', data);
      
      // Process users based on known API schema
      const processedUsers = data.map((user: any, index: number) => {
        console.log(`👤 Raw user ${index + 1}:`, user);
        
        // Find client name from clients array
        const client = clients.find(c => c.id === user.client_id);
        
        const processedUser = {
          id: user.id,
          name: user.username, // Use username as display name
          username: user.username,
          email: user.email,
          client_id: user.client_id,
          client_name: client?.name || `Client ${user.client_id}`,
          personalisation: user.personalisation,
          roles: user.roles || []
        };
        
        console.log(`✅ Processed user ${index + 1}:`, processedUser);
        return processedUser;
      });
      
      console.log('✅ Final processed users:', processedUsers);
      
      setUsers(processedUsers as User[]);
      setTotalRecords(processedUsers.length);
      setLastFetchTime(now);
      
      // Performance logging
      const loadTime = performance.now() - startTime;
      console.log(`⚡ Users loaded in ${loadTime.toFixed(2)}ms`);
      
      if (processedUsers.length === 0) {
        toast.current?.show({ 
          severity: 'info', 
          summary: 'No Users', 
          detail: 'No users found in the database', 
          life: 3000 
        });
      } else {
        toast.current?.show({ 
          severity: 'success', 
          summary: 'Users Loaded', 
          detail: `Successfully loaded ${processedUsers.length} users from database`, 
          life: 2000 
        });
      }
      
    } catch (error: any) {
      console.error('🚫 Unexpected error in loadUsers:', error);
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Load Error', 
        detail: 'Failed to load users. Please check console for details.', 
        life: 5000 
      });
    } finally {
      console.log('✅ Setting loading to false');
      setLoading(false);
    }
  }, [users.length, lastFetchTime, clients, loading]);

  // Initial load effect - runs only once
  useEffect(() => {
    console.log('🚀 Users component mounted - initializing...');
    console.log('📊 Initial state:', { 
      usersCount: users.length, 
      loading, 
      lastFetchTime 
    });
    
    // For development - set up test authentication
    if (process.env.NODE_ENV === 'development' && !sessionStorage.getItem('access_token')) {
      console.log('🔐 Setting up development authentication...');
      createTestToken().then(success => {
        if (success) {
          console.log('✅ Development authentication successful');
        } else {
          console.warn('⚠️ Development authentication failed - API calls may not work');
        }
      });
    }
    
    // Load reference data first (clients and roles)
    console.log('📞 Loading reference data...');
    loadClients();
    loadRoles();
    
    // Only load if we don't have users already
    if (users.length === 0) {
      console.log('📞 Loading users for the first time...');
      // Small delay to let clients load first for proper client name mapping
      setTimeout(() => loadUsers(undefined, true), 100);
    } else {
      console.log('⏭️ Users already loaded, skipping initial load');
    }
    
    console.log('🔧 Initializing filters...');
    initFilters();
    
    console.log('✅ Component initialization complete');
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Cache refresh effect - only refresh if explicitly needed
  useEffect(() => {
    if (lastFetchTime === 0) return; // Skip if no initial load yet
    
    // Only auto-refresh if users are empty (data loss scenario)
    if (users.length === 0 && lastFetchTime > 0) {
      console.log('⚠️ Users lost, reloading...');
      loadUsers(undefined, true);
    }
  }, [users.length, lastFetchTime, loadUsers]);

  // Memoized event handlers for better performance
  const onPage = useCallback((event: any) => {
    setLazyState(prevState => ({ ...prevState, ...event }));
    loadUsers(event);
  }, [loadUsers]);

  const onSort = useCallback((event: any) => {
    setLazyState(prevState => ({ ...prevState, ...event }));
    loadUsers(event);
  }, [loadUsers]);

  const onFilter = useCallback((event: any) => {
    setLazyState(prevState => ({ ...prevState, first: 0, ...event }));
    loadUsers(event);
  }, [loadUsers]);

  const openNew = () => {
    if (isMobile) {
      // Mobile: Use inline row addition
      startAddingNew();
    } else {
      // Desktop: Use modal dialog
      setUser({} as User);
      setSubmitted(false);
      setUserDialog(true);
    }
  };

  const startAddingNew = () => {
    setIsAddingNew(true);
    
    // Add temporary new row at the top
    const tempUser = { 
      id: 'temp-new', 
      name: '', 
      username: '', 
      email: '', 
      password: '', 
      client_id: clients.length > 0 ? clients[0].id : 1,
      client_name: clients.length > 0 ? clients[0].name : 'Client 1',
      roles: [] 
    };
    setUsers([tempUser, ...users]);
    
    // Set editing mode for the new row
    setEditingRows({ 'temp-new': true });
    
    toast.current?.show({ 
      severity: 'info', 
      summary: 'Add Mode', 
      detail: 'Fill in the details and click save', 
      life: 3000 
    });
  };

  const cancelAddingNew = () => {
    setIsAddingNew(false);
    
    // Remove temporary row
    setUsers(users.filter(u => u.id !== 'temp-new'));
    setEditingRows({});
    
    toast.current?.show({ 
      severity: 'info', 
      summary: 'Cancelled', 
      detail: 'New user creation cancelled', 
      life: 2000 
    });
  };

  const saveNewUser = async (rowData: User) => {
    try {
      // Validation
      const username = rowData.username || rowData.name;
      if (!username?.trim()) {
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Validation Error', 
          detail: 'Username/Name is required', 
          life: 3000 
        });
        return;
      }

      if (!rowData.email?.trim()) {
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Validation Error', 
          detail: 'Email is required', 
          life: 3000 
        });
        return;
      }

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(rowData.email)) {
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Validation Error', 
          detail: 'Invalid email format', 
          life: 3000 
        });
        return;
      }

      if (!rowData.password || rowData.password.length < 6) {
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Validation Error', 
          detail: 'Password is required and must be at least 6 characters long', 
          life: 3000 
        });
        return;
      }

      if (!rowData.client_id) {
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Validation Error', 
          detail: 'Client is required', 
          life: 3000 
        });
        return;
      }

      setLazyLoading(true);
      
      console.log('🔍 USER CREATE DEBUG - Starting user creation process');
      console.log('📋 Raw form data received:', {
        ...rowData,
        password: rowData.password ? '[PROVIDED]' : '[MISSING]'
      });
      
      // Create user via API - map frontend fields to backend schema
      const userCreateData = {
        username: username.trim(),
        email: rowData.email.trim(),
        password: rowData.password,
        client_id: parseInt(rowData.client_id.toString()),
        personalisation: rowData.personalisation || null
      };
      
      console.log('📤 Data being sent to backend:', {
        ...userCreateData,
        password: userCreateData.password ? '[PROVIDED]' : '[MISSING]'
      });
      console.log('🔐 Auth token present:', !!sessionStorage.getItem('access_token'));
      console.log('👤 Current user context:', JSON.parse(sessionStorage.getItem('user_data') || '{}'));
      
      console.log('📡 Calling createUser API...');
      const newUser = await createUser(userCreateData);
      console.log('✅ API call successful, received:', newUser);
      
      // Replace temporary row with real user data
      const updatedUsers = users.map(u => 
        u.id === 'temp-new' ? newUser : u
      );
      setUsers(updatedUsers);
      
      // Reset states
      setIsAddingNew(false);
      setEditingRows({});
      
      toast.current?.show({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'User created successfully', 
        life: 3000 
      });
    } catch (error: any) {
      console.error('❌ USER CREATE ERROR - Full error details:');
      console.error('🔍 Error object:', error);
      console.error('📡 HTTP status:', error.response?.status);
      console.error('📄 Response headers:', error.response?.headers);
      console.error('💾 Response data:', error.response?.data);
      console.error('🔧 Request config:', error.config);
      console.error('📤 Data that was sent:', {
        ...rowData,
        password: rowData.password ? '[PROVIDED]' : '[MISSING]'
      });
      console.error('🔐 Auth status at time of error:', {
        hasToken: !!sessionStorage.getItem('access_token'),
        userData: sessionStorage.getItem('user_data')
      });
      
      let errorMessage = 'Failed to create user';
      if (error.response?.data?.detail) {
        console.log('📋 Parsing backend validation errors...');
        if (Array.isArray(error.response.data.detail)) {
          console.log('📝 Validation errors:', error.response.data.detail);
          errorMessage = error.response.data.detail.map((err: any) => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
        } else {
          console.log('📝 Error detail:', error.response.data.detail);
          errorMessage = error.response.data.detail;
        }
      } else if (error.message) {
        console.log('📝 Error message:', error.message);
        errorMessage = error.message;
      }
      
      console.error('📢 Final error message shown to user:', errorMessage);
      
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Error Creating User', 
        detail: errorMessage, 
        life: 5000 
      });
    } finally {
      setLazyLoading(false);
    }
  };

  const hideDialog = () => {
    setSubmitted(false);
    setUserDialog(false);
  };

  const saveUser = async () => {
    setSubmitted(true);

    // Validate required fields
    if (!(user.name || user.username)?.trim()) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Validation Error', 
        detail: 'Name is required', 
        life: 3000 
      });
      return;
    }

    if (!user.client_id) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Validation Error', 
        detail: 'Client is required', 
        life: 3000 
      });
      return;
    }

    // For new users, validate required fields
    if (!user.id) {
      if (!user.password || user.password.length < 6) {
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Validation Error', 
          detail: 'Password is required and must be at least 6 characters long', 
          life: 3000 
        });
        return;
      }

      if (!user.email?.trim()) {
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Validation Error', 
          detail: 'Email is required', 
          life: 3000 
        });
        return;
      }

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.email)) {
        toast.current?.show({ 
          severity: 'error', 
          summary: 'Validation Error', 
          detail: 'Invalid email format', 
          life: 3000 
        });
        return;
      }
    }

    if ((user.name || user.username)?.trim()) {
      try {
        let _users = [...users];
        let _user = { ...user };

        if (user.id) {
          // Update existing user
          const updatedUser = await updateUser(user.id, _user);
          const index = _users.findIndex(u => u.id === user.id);
          _users[index] = updatedUser;
          toast.current?.show({ severity: 'success', summary: 'Successful', detail: 'User Updated', life: 3000 });
        } else {
          // Create new user - map to backend schema
          console.log('🔍 SAVEUSER CREATE - Raw user data:', { ..._user, password: _user.password ? '[PROVIDED]' : '[MISSING]' });
          
          const userCreateData = {
            username: (_user.username || _user.name)?.trim(),
            email: _user.email?.trim(),
            password: _user.password,
            client_id: parseInt(_user.client_id?.toString() || '0'),
            personalisation: _user.personalisation || null
          };
          
          console.log('📤 SAVEUSER CREATE - Data being sent to backend:', {
            ...userCreateData,
            password: userCreateData.password ? '[PROVIDED]' : '[MISSING]'
          });
          
          const newUser = await createUser(userCreateData);
          _users.push(newUser);
          toast.current?.show({ severity: 'success', summary: 'Successful', detail: 'User Created', life: 3000 });
        }

        setUsers(_users);
        setUserDialog(false);
        setUser({} as User);
      } catch (error: any) {
        toast.current?.show({ severity: 'error', summary: 'Error', detail: error.message, life: 3000 });
      }
    }
  };

  const deleteUserConfirmed = useCallback(async (user: User) => {
    const originalUsers = [...users];
    try {
      // Optimistic update
      setUsers(users.filter(u => u.id !== user.id));
      
      toast.current?.show({ 
        severity: 'info', 
        summary: 'Deleting...', 
        detail: 'User deletion in progress', 
        life: 2000 
      });
      
      await deleteUser(user.id);
      
      toast.current?.show({ 
        severity: 'success', 
        summary: 'Deleted', 
        detail: 'User deleted successfully', 
        life: 3000 
      });
    } catch (error: any) {
      // Revert optimistic update on error
      setUsers(originalUsers);
      
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Delete Failed', 
        detail: error.message || 'Failed to delete user', 
        life: 5000 
      });
    }
  }, [users]);

  const confirmDeleteUser = useCallback((user: User) => {
    confirmDialog({
      message: 'Are you sure you want to delete this user?',
      header: 'Confirm',
      icon: 'pi pi-exclamation-triangle',
      accept: () => deleteUserConfirmed(user)
    });
  }, [deleteUserConfirmed]);

  const deleteSelectedUsers = useCallback(async () => {
    if (selectedUsers.length === 0) return;
    
    const originalUsers = [...users];
    const originalSelectedUsers = [...selectedUsers];
    
    try {
      // Optimistic update
      const remainingUsers = users.filter(u => !selectedUsers.some(selected => selected.id === u.id));
      setUsers(remainingUsers);
      setSelectedUsers([]);
      
      toast.current?.show({ 
        severity: 'info', 
        summary: 'Deleting...', 
        detail: `Deleting ${originalSelectedUsers.length} users`, 
        life: 2000 
      });
      
      // Batch delete with concurrency limit
      const batchSize = 5;
      for (let i = 0; i < originalSelectedUsers.length; i += batchSize) {
        const batch = originalSelectedUsers.slice(i, i + batchSize);
        await Promise.all(batch.map(user => deleteUser(user.id)));
      }
      
      toast.current?.show({ 
        severity: 'success', 
        summary: 'Success', 
        detail: `${originalSelectedUsers.length} users deleted successfully`, 
        life: 3000 
      });
    } catch (error: any) {
      // Revert optimistic update on error
      setUsers(originalUsers);
      setSelectedUsers(originalSelectedUsers);
      
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Bulk Delete Failed', 
        detail: error.message || 'Failed to delete users', 
        life: 5000 
      });
    }
  }, [selectedUsers, users]);

  const confirmDeleteSelected = useCallback(() => {
    confirmDialog({
      message: `Are you sure you want to delete ${selectedUsers.length} selected user(s)?`,
      header: 'Confirm Bulk Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: () => deleteSelectedUsers()
    });
  }, [selectedUsers, deleteSelectedUsers]);

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>, name: string) => {
    const val = (e.target && e.target.value) || '';
    let _user = { ...user };
    (_user as any)[name] = val;
    setUser(_user);
  };

  const onDropdownChange = (value: any, name: string) => {
    let _user = { ...user };
    (_user as any)[name] = value;
    setUser(_user);
  };

  const resetPassword = async () => {
    if (!newPassword || newPassword !== confirmPassword) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Validation Error', 
        detail: 'Passwords do not match or are empty', 
        life: 3000 
      });
      return;
    }

    if (newPassword.length < 6) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Validation Error', 
        detail: 'Password must be at least 6 characters long', 
        life: 3000 
      });
      return;
    }

    try {
      await resetUserPassword(selectedUserForReset.id, newPassword);
      
      toast.current?.show({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Password reset successfully', 
        life: 3000 
      });
      
      hidePasswordResetDialog();
    } catch (error: any) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Reset Failed', 
        detail: error.message || 'Failed to reset password', 
        life: 5000 
      });
    }
  };

  const showPasswordResetDialog = (userData: User) => {
    setSelectedUserForReset(userData);
    setNewPassword('');
    setConfirmPassword('');
    setPasswordResetDialog(true);
  };

  const hidePasswordResetDialog = () => {
    setPasswordResetDialog(false);
    setNewPassword('');
    setConfirmPassword('');
    setSelectedUserForReset({} as User);
  };



  // Enhanced inline editing functions
  const onRowEditComplete = async (e: any) => {
    let { newData, index } = e;
    
    // Handle new user creation
    if (newData.id === 'temp-new') {
      await saveNewUser(newData);
      return;
    }
    
    // Validation for existing users
    if (!newData.name?.trim() && !newData.username?.trim()) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Validation Error', 
        detail: 'Name is required', 
        life: 3000 
      });
      return;
    }

    // For new users, validate password
    if (newData.id === 'temp-new' && (!newData.password || newData.password.length < 6)) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Validation Error', 
        detail: 'Password is required and must be at least 6 characters long', 
        life: 3000 
      });
      return;
    }

    if (newData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newData.email)) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Validation Error', 
        detail: 'Invalid email format', 
        life: 3000 
      });
      return;
    }

    try {
      setLazyLoading(true);
      
      // Update client_name if client_id changed
      if (newData.client_id) {
        const selectedClient = clients.find(c => c.id === newData.client_id);
        if (selectedClient) {
          newData.client_name = selectedClient.name;
        }
      }
      
      // Filter data to match backend UserUpdate schema (for PUT requests)
      // Omit password field entirely for inline edits
      const updateData = {
        username: newData.username || newData.name,
        email: newData.email,
        client_id: newData.client_id,
        personalisation: newData.personalisation || null
      };
      
      console.log('🔍 INLINE EDIT - Original data:', newData);
      console.log('📤 INLINE EDIT - Filtered data being sent:', updateData);
      
      // Update user via API
      const updatedUser = await updateUser(newData.id, updateData);
      
      // Update local state
      let _users = [...users];
      _users[index] = updatedUser;
      setUsers(_users);
      
      toast.current?.show({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'User updated successfully', 
        life: 3000 
      });
      
      // Clear editing state for this row
      const newEditingRows = {...editingRows};
      delete newEditingRows[newData.id];
      setEditingRows(newEditingRows);
    } catch (error: any) {
      toast.current?.show({ 
        severity: 'error', 
        summary: 'Error', 
        detail: error.message, 
        life: 3000 
      });
    } finally {
      setLazyLoading(false);
    }
  };

  // Enhanced cell editor components
  const textEditor = (options: ColumnEditorOptions) => {
    return (
      <InputText 
        type="text" 
        value={options.value || ''} 
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          const newValue = e.target.value;
          options.editorCallback!(newValue);
          
          // For new users, also update username field when name changes
          if (options.rowData.id === 'temp-new' && options.field === 'name') {
            const updatedUsers = users.map(user => {
              if (user.id === 'temp-new') {
                return { ...user, username: newValue };
              }
              return user;
            });
            setUsers(updatedUsers);
          }
        }} 
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.stopPropagation();
          }
        }}
        autoFocus
        className="w-full"
        placeholder="Enter name..."
      />
    );
  };

  const emailEditor = (options: ColumnEditorOptions) => {
    const validateEmail = (email: string) => {
      if (!email) return true;
      return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email);
    };

    return (
      <InputText 
        type="email" 
        value={options.value || ''} 
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          const value = e.target.value;
          options.editorCallback!(value);
        }} 
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.stopPropagation();
          }
        }}
        className={`w-full ${options.value && !validateEmail(options.value) ? 'p-invalid' : ''}`}
        placeholder="Enter email..."
      />
    );
  };

  const clientEditor = (options: ColumnEditorOptions) => {
    return (
      <Dropdown 
        value={options.value} 
        options={clients}
        optionLabel="name"
        optionValue="id"
        onChange={(e) => {
          // Update both client_id and client_name
          options.editorCallback!(e.value);
          // Note: For inline editing, we'd need to update the client_name too
          // This is handled in the onRowEditComplete function
        }} 
        placeholder="Select Client"
        className="w-full"
        filter
        showClear
      />
    );
  };

  const rolesEditor = (options: ColumnEditorOptions) => {
    return (
      <MultiSelect 
        value={options.value || []} 
        options={roles}
        optionLabel="name"
        optionValue="name"
        onChange={(e) => options.editorCallback!(e.value)} 
        placeholder="Select Roles"
        className="w-full"
        filter
        maxSelectedLabels={3}
        selectedItemsLabel="{0} roles selected"
      />
    );
  };

  const passwordEditor = (options: ColumnEditorOptions) => {
    return (
      <Password
        value={options.value || ''}
        onChange={(e) => options.editorCallback!(e.target.value)}
        placeholder="Enter password"
        toggleMask
        feedback={false}
        className="w-full"
      />
    );
  };

  // Memoized filter functions
  const defaultFilters = useMemo(() => ({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    name: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    email: { value: null, matchMode: FilterMatchMode.CONTAINS },
    client_name: { value: null, matchMode: FilterMatchMode.CONTAINS },
    roles: { value: null, matchMode: FilterMatchMode.CONTAINS }
  }), []);

  const initFilters = useCallback(() => {
    setFilters(defaultFilters);
    setGlobalFilter('');
  }, [defaultFilters]);

  const clearFilter = useCallback(() => {
    initFilters();
    toast.current?.show({ 
      severity: 'info', 
      summary: 'Filters Cleared', 
      detail: 'All filters have been reset', 
      life: 2000 
    });
  }, [initFilters]);

  const onGlobalFilterChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setGlobalFilter(value);
    
    // Update filters immediately for UI responsiveness
    let _filters = { ...filters };
    (_filters['global'] as any).value = value;
    setFilters(_filters);
    
    // Use debounced search for performance
    debouncedSearch(value);
  }, [filters, debouncedSearch]);

  // Memoized toolbar template for performance
  const leftToolbarTemplate = useMemo(() => {
    const getButtonLabel = (fullLabel: string, shortLabel: string) => {
      if (screenSize === 'mobile') return shortLabel;
      if (screenSize === 'tablet') return shortLabel;
      return fullLabel;
    };

    return (
      <div className="flex flex-wrap gap-2">
        <Button 
          label={getButtonLabel("New User", "Add")} 
          icon="pi pi-plus" 
          severity="success" 
          onClick={openNew}
          disabled={isAddingNew}
          size={screenSize === 'mobile' ? "small" : undefined}
          tooltip={screenSize === 'mobile' ? "Add new user" : undefined}
        />
        {isAddingNew && (
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            outlined 
            onClick={cancelAddingNew}
            size={screenSize === 'mobile' ? "small" : undefined}
            tooltip={screenSize === 'mobile' ? "Cancel adding user" : undefined}
          />
        )}
        <Button
          label={getButtonLabel("Delete Selected", "Delete")}
          icon="pi pi-trash"
          severity="danger"
          onClick={confirmDeleteSelected}
          disabled={!selectedUsers || !selectedUsers.length || isAddingNew}
          size={screenSize === 'mobile' ? "small" : undefined}
          tooltip={screenSize === 'mobile' ? `Delete ${selectedUsers.length} selected` : undefined}
        />
      </div>
    );
  }, [screenSize, isAddingNew, selectedUsers.length, selectedUsers, openNew, cancelAddingNew, confirmDeleteSelected]);

  const rightToolbarTemplate = () => {
    return (
      <div className="flex align-items-center justify-content-end gap-2">
        <Button
          icon="pi pi-refresh"
          severity="info"
          outlined
          onClick={() => {
            console.log('🔄 Manual refresh triggered');
            loadUsers(undefined, true);
          }}
          tooltip="Refresh Users"
          size={screenSize === 'mobile' ? 'small' : undefined}
          loading={loading}
        />
        <Button 
          label="Reset Password" 
          icon="pi pi-key" 
          severity="warning" 
          outlined
          onClick={() => {
            if (selectedUsers && selectedUsers.length === 1) {
              showPasswordResetDialog(selectedUsers[0]);
            } else {
              toast.current?.show({ 
                severity: 'warn', 
                summary: 'Selection Required', 
                detail: 'Please select exactly one user to reset password', 
                life: 3000 
              });
            }
          }}
          disabled={!selectedUsers || selectedUsers.length !== 1}
          size={screenSize === 'mobile' ? 'small' : undefined}
        />
        <Button label="Export" icon="pi pi-upload" className="p-button-help" onClick={() => dt.current?.exportCSV()} />
      </div>
    );
  };

  // Memoized action body template for non-editing actions
  const actionBodyTemplate = useCallback((rowData: User) => {
    // Show only delete button (edit is handled by PrimeReact's rowEditor)
    return (
      <div className="flex gap-1">
        <Button 
          icon="pi pi-trash" 
          rounded 
          outlined 
          severity="danger" 
          size="small"
          onClick={() => confirmDeleteUser(rowData)}
          tooltip="Delete User"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  }, [confirmDeleteUser]);

  const header = (
    <div className="flex flex-wrap gap-2 align-items-center justify-content-between">
      <div className="flex align-items-center gap-2">
        <h4 className="m-0">Manage Users</h4>
        <Button type="button" icon="pi pi-filter-slash" label="Clear" outlined onClick={clearFilter} />
      </div>
      <div className="flex gap-2">
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText
            value={globalFilter}
            onChange={onGlobalFilterChange}
            placeholder="Global Search"
          />
        </span>
      </div>
    </div>
  );

  const userDialogFooter = (
    <div>
      <Button label="Cancel" icon="pi pi-times" outlined onClick={hideDialog} />
      <Button label="Save" icon="pi pi-check" onClick={saveUser} />
    </div>
  );



  // Performance monitoring and key debugging
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 Users state changed:', { 
        count: users.length, 
        users: users.map(u => ({ id: u.id, name: u.name })),
        selectedCount: selectedUsers.length 
      });
      
      // Check for duplicate IDs
      const ids = users.map(u => u.id);
      const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
      if (duplicateIds.length > 0) {
        console.error('🚨 DUPLICATE IDs FOUND:', duplicateIds);
      }
      
      const interval = setInterval(() => {
        console.log('🔍 Memory Usage:', getMemoryUsage());
        console.log('👥 Users Count:', users.length);
        console.log('🔧 Selected Count:', selectedUsers.length);
      }, 30000); // Every 30 seconds
      
      return () => clearInterval(interval);
    }
  }, [users, selectedUsers.length]);

  return (
    <UserTableErrorBoundary>
      <div className="users-container">
        <Toast ref={toast} />
        <ConfirmDialog />
        
        {process.env.NODE_ENV === 'development' && (
          <div key="debug-info" className="p-2 mb-2 text-xs bg-gray-100 rounded">
            🚀 Performance: {users.length} users | Selected: {selectedUsers.length} | 
            Last Updated: {new Date(lastFetchTime).toLocaleTimeString()}
          </div>
        )}

        <div className="card">
          <Toolbar className="mb-4" left={leftToolbarTemplate} right={rightToolbarTemplate}></Toolbar>

        <DataTable
          key={`users-datatable-${users.length}-${users.map(u => u.id).join('-')}`}
          ref={dt}
          value={users}
          selection={selectedUsers}
          onSelectionChange={(e) => setSelectedUsers(e.value as User[])}
          selectionMode="multiple"
          dataKey="id"
          editMode="row"
          editingRows={editingRows}
          onRowEditInit={(e) => {
            const newEditingRows = {...editingRows, [e.data.id]: true};
            setEditingRows(newEditingRows);
          }}
          onRowEditCancel={(e) => {
            const newEditingRows = {...editingRows};
            delete newEditingRows[e.data.id];
            setEditingRows(newEditingRows);
            
            // Remove temp row if canceling new user creation
            if (e.data.id === 'temp-new') {
              setUsers(users.filter(u => u.id !== 'temp-new'));
              setIsAddingNew(false);
            }
          }}
          onRowEditComplete={onRowEditComplete}
          rowClassName={(data) => {
            // Debug row data
            if (process.env.NODE_ENV === 'development') {
              console.log('🏠 Row data:', data?.id, data?.name);
            }
            return '';
          }}
          lazy={false}
          paginator
          first={lazyState.first}
          rows={screenSize === 'mobile' ? 5 : lazyState.rows}
          totalRecords={totalRecords}
          onPage={onPage}
          onSort={onSort}
          onFilter={onFilter}
          sortField={lazyState.sortField}
          sortOrder={lazyState.sortOrder as 1 | -1 | 0 | null | undefined}
          rowsPerPageOptions={screenSize === 'mobile' ? [5, 10, 15] : [5, 10, 25, 50]}
          paginatorTemplate={screenSize === 'mobile' ? 
            "PrevPageLink PageLinks NextPageLink" : 
            "FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          }
          currentPageReportTemplate="{first}-{last} of {totalRecords}"
          filters={filters}
          filterDisplay="row"
          globalFilterFields={['name', 'username', 'email']}
          header={header}
          loading={loading || lazyLoading}
          scrollable
          scrollHeight={screenSize === 'mobile' ? '400px' : '600px'}
          stripedRows={screenSize !== 'mobile'}
          showGridlines={screenSize !== 'mobile'}
          className="p-datatable-sm"
        >
          <Column 
            key="selection"
            selectionMode="multiple" 
            exportable={false}
            style={{ minWidth: '3rem', maxWidth: '3rem' }}
            frozen
          ></Column>
          <Column 
            key="id"
            field="id" 
            header="ID" 
            sortable 
            filter 
            filterPlaceholder="Search by ID"
            style={{ minWidth: '6rem', maxWidth: '8rem' }}
            frozen
          ></Column>
          <Column
            key="name"
            field="name"
            header="Name"
            sortable
            filter
            filterPlaceholder="Search by name"
            style={{ minWidth: '12rem', flex: '1 1 200px' }}
            body={(rowData) => {
              const displayName = rowData.name || rowData.username || '';
              return (
                <div className="flex align-items-center gap-2">
                  <span style={{ fontWeight: 'bold' }}>
                    {displayName}
                  </span>
                </div>
              );
            }}
            editor={(options) => textEditor(options)}
          ></Column>
          <Column 
            key="email"
            field="email" 
            header="Email" 
            sortable 
            filter 
            filterPlaceholder="Search by email"
            style={{ minWidth: '15rem', flex: '1 1 250px' }}
            editor={(options) => emailEditor(options)}
            body={(rowData) => {
              if (rowData.email) {
                return (
                  <span className="text-blue-600 hover:text-blue-800 cursor-pointer"
                        onClick={() => window.open(`mailto:${rowData.email}`)}>
                    {rowData.email}
                  </span>
                );
              }
              return <span className="text-gray-400">No email</span>;
            }}
          ></Column>
          <Column 
            key="client_name"
            field="client_name" 
            header="Client" 
            sortable 
            filter 
            filterPlaceholder="Search by client"
            style={{ minWidth: '12rem', flex: '1 1 150px' }}
            editor={(options) => clientEditor(options)}
            body={(rowData) => {
              return rowData.client_name || `Client ${rowData.client_id || 'Unknown'}`;
            }}
          ></Column>
          <Column 
            key="roles"
            field="roles" 
            header="Roles" 
            sortable 
            filter 
            filterPlaceholder="Search by roles"
            style={{ minWidth: '15rem', flex: '1 1 200px' }}
            editor={(options) => rolesEditor(options)}
            body={(rowData) => {
              if (Array.isArray(rowData.roles) && rowData.roles.length > 0) {
                return (
                  <div className="flex flex-wrap gap-1">
                    {rowData.roles.map((role: string, index: number) => (
                      <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {role}
                      </span>
                    ))}
                  </div>
                );
              }
              return <span className="text-gray-400">No roles</span>;
            }}
          ></Column>
          {(users.some(u => u.id === 'temp-new') || isAddingNew) && (
            <Column 
              key="password"
              field="password" 
              header="Password" 
              style={{ minWidth: '12rem', flex: '1 1 150px' }}
              editor={(options) => passwordEditor(options)}
              body={(rowData) => {
                // Only show password field for new users being added
                if (rowData.id === 'temp-new') {
                  return <span className="text-gray-400">Enter password...</span>;
                }
                return <span className="text-gray-400">••••••••</span>;
              }}
            ></Column>
          )}
          <Column 
            key="row-editor"
            rowEditor={true}
            header="Edit"
            exportable={false} 
            style={{ minWidth: '6rem', maxWidth: '6rem' }}
            frozen
            alignFrozen="right"
          ></Column>
          <Column 
            key="actions"
            header="Actions"
            body={actionBodyTemplate} 
            exportable={false} 
            style={{ minWidth: '5rem', maxWidth: '5rem' }}
            frozen
            alignFrozen="right"
          ></Column>
        </DataTable>
      </div>

      <Dialog
        visible={userDialog}
        style={{ width: '450px' }}
        header="User Details"
        modal
        className="p-fluid"
        footer={userDialogFooter}
        onHide={hideDialog}
      >
        <div className="field">
          <label htmlFor="name">Name</label>
          <InputText
            id="name"
            value={user.name || user.username || ''}
            onChange={(e) => onInputChange(e, 'name')}
            required
            autoFocus
            className={submitted && !(user.name || user.username) ? 'p-invalid' : ''}
          />
          {submitted && !(user.name || user.username) && <small className="p-error">Name is required.</small>}
        </div>
        
        <div className="field">
          <label htmlFor="email">Email</label>
          <InputText
            id="email"
            value={user.email || ''}
            onChange={(e) => onInputChange(e, 'email')}
          />
        </div>
        
        <div className="field">
          <label htmlFor="client_id">Client</label>
          <Dropdown
            id="client_id"
            value={user.client_id}
            options={clients}
            optionLabel="name"
            optionValue="id"
            onChange={(e) => onDropdownChange(e.value, 'client_id')}
            placeholder="Select a client"
            filter
            showClear
            className={submitted && !user.client_id ? 'p-invalid' : ''}
          />
          {submitted && !user.client_id && <small className="p-error">Client is required.</small>}
        </div>
        
        <div className="field">
          <label htmlFor="roles">Roles</label>
          <MultiSelect
            id="roles"
            value={user.roles || []}
            options={roles}
            optionLabel="name"
            optionValue="name"
            onChange={(e) => onDropdownChange(e.value, 'roles')}
            placeholder="Select roles"
            filter
            maxSelectedLabels={3}
            selectedItemsLabel="{0} roles selected"
          />
        </div>
        
        {(!user.id || user.id === 'new') && (
          <div className="field">
            <label htmlFor="password">Password *</label>
            <Password
              id="password"
              value={user.password || ''}
              onChange={(e) => onInputChange(e as any, 'password')}
              placeholder="Enter password (min 6 characters)"
              toggleMask
              feedback={true}
              promptLabel="Enter a password"
              weakLabel="Weak"
              mediumLabel="Medium"
              strongLabel="Strong"
              className={submitted && (!user.password || user.password.length < 6) ? 'p-invalid' : ''}
            />
            {submitted && (!user.password || user.password.length < 6) && (
              <small className="p-error">Password is required and must be at least 6 characters long.</small>
            )}
          </div>
        )}
      </Dialog>

      <Dialog
        visible={passwordResetDialog}
        style={{ width: '450px' }}
        header={`Reset Password for ${selectedUserForReset.name || selectedUserForReset.username}`}
        modal
        className="p-fluid"
        footer={
          <div>
            <Button 
              label="Cancel" 
              icon="pi pi-times" 
              outlined 
              onClick={hidePasswordResetDialog} 
            />
            <Button 
              label="Reset Password" 
              icon="pi pi-check" 
              onClick={resetPassword}
              disabled={!newPassword || !confirmPassword || newPassword !== confirmPassword}
            />
          </div>
        }
        onHide={hidePasswordResetDialog}
      >
        <div className="field">
          <label htmlFor="newPassword">New Password *</label>
          <Password
            id="newPassword"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Enter new password"
            toggleMask
            feedback={true}
            promptLabel="Enter a password"
            weakLabel="Weak"
            mediumLabel="Medium"
            strongLabel="Strong"
          />
        </div>
        
        <div className="field">
          <label htmlFor="confirmPassword">Confirm Password *</label>
          <Password
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password"
            toggleMask
            feedback={false}
            className={confirmPassword && newPassword !== confirmPassword ? 'p-invalid' : ''}
          />
          {confirmPassword && newPassword !== confirmPassword && (
            <small className="p-error">Passwords do not match.</small>
          )}
        </div>
        
        <div className="field">
          <small className="text-gray-600">
            💡 Password requirements:
            <ul className="mt-1 ml-4">
              <li>• Minimum 6 characters</li>
              <li>• Consider using a mix of letters, numbers, and symbols</li>
            </ul>
          </small>
        </div>
      </Dialog>
      </div>
    </UserTableErrorBoundary>
  );
}
