#!/bin/bash
# Frontend Behavior Test Suite
# This script simulates the exact frontend behavior to reproduce the menu disappearing issue

echo "🧪 FRONTEND BEHAVIOR TEST SUITE"
echo "=============================="
echo ""

BASE_URL="http://localhost:8001/api/v1"

# Test Case 1: Login Flow Simulation
test_login_flow() {
    echo "TEST 1: Login Flow Simulation"
    echo "----------------------------"
    
    echo "Step 1.1: Login to get token..."
    TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=superadmin&password=superadmin123")
    
    if [[ $? -ne 0 ]]; then
        echo "❌ Login failed"
        return 1
    fi
    
    TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    
    if [[ -z "$TOKEN" ]]; then
        echo "❌ No token received"
        echo "Response: $TOKEN_RESPONSE"
        return 1
    fi
    
    echo "✅ Token received: ${TOKEN:0:50}..."
    
    echo ""
    echo "Step 1.2: Call /auth/me (what updated login() does)..."
    USER_RESPONSE=$(curl -s "$BASE_URL/auth/me" -H "Authorization: Bearer $TOKEN")
    
    if [[ $? -ne 0 ]]; then
        echo "❌ /auth/me failed"
        return 1
    fi
    
    echo "✅ User profile: $USER_RESPONSE"
    
    echo ""
    echo "Step 1.3: Simulate AuthContext state change..."
    echo "  - isAuthenticated: true"
    echo "  - isLoading: false" 
    echo "  - user: $(echo $USER_RESPONSE | python3 -c "import sys, json; u=json.load(sys.stdin); print(f\"{u['username']} ({u['roles'][0]})\")" 2>/dev/null)"
    
    echo ""
    echo "Step 1.4: NavBar should mount → Start permission loading..."
    echo "  - NavBar permissions loading: true"
    echo "  - hasAccess() using fallback logic"
    
    return 0
}

# Test Case 2: Permission Loading Simulation  
test_permission_loading() {
    echo ""
    echo "TEST 2: Permission Loading Simulation"
    echo "-----------------------------------"
    
    if [[ -z "$TOKEN" ]]; then
        echo "❌ No token available, run test_login_flow first"
        return 1
    fi
    
    # Simulate the screens that NavBar checks
    SCREENS=(
        "/dashboard"
        "/invoices"
        "/suppliers"
        "/business-units"
        "/regions"
        "/roles"
        "/users"
        "/clients"
        "/subcategories"
        "/unit-of-measure"
        "/currency"
        "/import-errors"
        "/reporting"
        "/client-settings"
        "/settings"
        "/screen-permissions"
    )
    
    echo "Step 2.1: Check permissions for all screens (what useMultiplePermissions does)..."
    
    FALLBACK_SCREENS=()
    ACTUAL_SCREENS=()
    
    # Simulate fallback logic for superadmin during loading
    echo ""
    echo "Step 2.2: Fallback permissions (during loading):"
    for screen in "${SCREENS[@]}"; do
        case $screen in
            "/dashboard"|"/invoices"|"/suppliers")
                echo "  ✅ $screen (basic access)"
                FALLBACK_SCREENS+=("$screen")
                ;;
            "/clients"|"/roles"|"/users"|"/screen-permissions"|"/settings")
                echo "  ✅ $screen (superadmin access)"
                FALLBACK_SCREENS+=("$screen")
                ;;
            *)
                echo "  ❌ $screen (fallback deny)"
                ;;
        esac
    done
    
    echo ""
    echo "Step 2.3: Actual permissions (after API calls):"
    for screen in "${SCREENS[@]}"; do
        PERM_RESPONSE=$(curl -s "$BASE_URL/screen-permissions/check?screen_route=$screen&action=view" \
            -H "Authorization: Bearer $TOKEN")
        
        HAS_PERM=$(echo $PERM_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['has_permission'])" 2>/dev/null)
        
        if [[ "$HAS_PERM" == "True" ]]; then
            echo "  ✅ $screen"
            ACTUAL_SCREENS+=("$screen")
        else
            echo "  ❌ $screen"
        fi
    done
    
    echo ""
    echo "Step 2.4: Compare fallback vs actual permissions..."
    echo "Fallback screens: ${#FALLBACK_SCREENS[@]} items"
    echo "Actual screens: ${#ACTUAL_SCREENS[@]} items"
    
    # Check for differences
    DIFFERENT=false
    for screen in "${FALLBACK_SCREENS[@]}"; do
        if [[ ! " ${ACTUAL_SCREENS[@]} " =~ " $screen " ]]; then
            echo "⚠️  DIFFERENCE: $screen in fallback but not in actual"
            DIFFERENT=true
        fi
    done
    
    for screen in "${ACTUAL_SCREENS[@]}"; do
        if [[ ! " ${FALLBACK_SCREENS[@]} " =~ " $screen " ]]; then
            echo "⚠️  DIFFERENCE: $screen in actual but not in fallback"
            DIFFERENT=true
        fi
    done
    
    if [[ "$DIFFERENT" == "true" ]]; then
        echo ""
        echo "🔍 ROOT CAUSE IDENTIFIED:"
        echo "   Fallback permissions ≠ Actual permissions"
        echo "   This causes menu items to appear/disappear when loading finishes!"
    else
        echo ""
        echo "✅ Fallback and actual permissions match"
    fi
    
    return 0
}

# Test Case 3: Timing Simulation
test_timing_simulation() {
    echo ""
    echo "TEST 3: Timing Simulation"
    echo "------------------------"
    
    echo "Step 3.1: Simulate rapid state changes..."
    echo "  T+0ms: Login success → AuthContext.isLoading = false"
    echo "  T+1ms: NavBar mounts → useMultiplePermissions.loading = true"
    echo "  T+2ms: NavBar renders with fallback permissions"
    echo "  T+100ms: First permission API call completes"
    echo "  T+200ms: Second permission API call completes"
    echo "  T+500ms: All permissions loaded → loading = false"
    echo "  T+501ms: NavBar re-renders with actual permissions"
    
    echo ""
    echo "Step 3.2: Check if this timing causes menu disappearance..."
    
    # Measure actual API response times
    echo "Measuring actual API response times..."
    
    for i in {1..3}; do
        START_TIME=$(date +%s%3N)
        curl -s "$BASE_URL/screen-permissions/check?screen_route=/dashboard&action=view" \
            -H "Authorization: Bearer $TOKEN" > /dev/null
        END_TIME=$(date +%s%3N)
        DURATION=$((END_TIME - START_TIME))
        echo "  API call $i: ${DURATION}ms"
    done
    
    return 0
}

# Test Case 4: State Change Logging
test_state_logging() {
    echo ""
    echo "TEST 4: State Change Analysis"
    echo "---------------------------"
    
    echo "This would require frontend instrumentation to track:"
    echo "  - AuthContext state changes"
    echo "  - NavBar mount/unmount events"  
    echo "  - useMultiplePermissions state changes"
    echo "  - hasAccess() return value changes"
    echo "  - navigationItems array changes"
    echo ""
    echo "Recommendation: Add console.log statements to track these state changes"
    
    return 0
}

# Main execution
main() {
    echo "Starting frontend behavior analysis..."
    echo ""
    
    # Check if backend is running
    if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        echo "❌ Backend not running on $BASE_URL"
        echo "Please start the backend server first"
        exit 1
    fi
    
    echo "✅ Backend is running"
    echo ""
    
    # Run tests
    test_login_flow
    if [[ $? -eq 0 ]]; then
        test_permission_loading
        test_timing_simulation
        test_state_logging
    fi
    
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "1. Add detailed logging to frontend components"
    echo "2. Test with browser developer tools open"
    echo "3. Record exact timing of state changes"
    echo "4. Implement fix based on findings"
}

# Run the tests
main "$@"