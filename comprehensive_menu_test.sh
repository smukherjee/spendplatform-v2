#!/bin/bash
# Comprehensive test to debug menu disappearing issue

echo "🔍 MENU DISAPPEARING DEBUG TEST"
echo "================================"

BASE_URL="http://localhost:8001/api/v1"

# Step 1: Check if backend is running
echo "1. Checking backend availability..."
curl -s -X POST "$BASE_URL/auth/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=test&password=test" > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    echo "✅ Backend is running at $BASE_URL"
else
    echo "❌ Backend is NOT running at $BASE_URL"
    exit 1
fi

# Step 2: Test login flow
echo ""
echo "2. Testing login flow..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=superadmin&password=superadmin123")

echo "Token response: $TOKEN_RESPONSE"

TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [[ -z "$TOKEN" ]]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Token received (length: ${#TOKEN})"

# Step 3: Test /auth/me endpoint  
echo ""
echo "3. Testing /auth/me endpoint..."
USER_RESPONSE=$(curl -s "$BASE_URL/auth/me" \
    -H "Authorization: Bearer $TOKEN")

echo "User response: $USER_RESPONSE"

# Step 4: Test permission checking for ALL screens
echo ""
echo "4. Testing permission checks for all screens..."
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

ACCESSIBLE_SCREENS=()
INACCESSIBLE_SCREENS=()

for screen in "${SCREENS[@]}"; do
    echo -n "  Checking $screen... "
    
    RESPONSE=$(curl -s "$BASE_URL/screen-permissions/check?screen_route=$screen&action=view" \
        -H "Authorization: Bearer $TOKEN")
    
    HAS_ACCESS=$(echo $RESPONSE | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('true' if data.get('has_access', False) else 'false')
except:
    print('error')
" 2>/dev/null)
    
    if [[ "$HAS_ACCESS" == "true" ]]; then
        echo "✅ ACCESSIBLE"
        ACCESSIBLE_SCREENS+=("$screen")
    elif [[ "$HAS_ACCESS" == "false" ]]; then
        echo "❌ NOT ACCESSIBLE"
        INACCESSIBLE_SCREENS+=("$screen")
    else
        echo "⚠️  ERROR: $RESPONSE"
    fi
done

# Step 5: Analyze fallback logic vs actual permissions
echo ""
echo "5. FALLBACK vs ACTUAL ANALYSIS"
echo "==============================="

# Fallback screens for superadmin during loading
FALLBACK_SCREENS=(
    "/dashboard"      # Always shown
    "/invoices"       # Always shown  
    "/suppliers"      # Always shown
    "/clients"        # Superadmin specific
    "/roles"          # Superadmin specific
    "/users"          # Superadmin specific
    "/screen-permissions"  # Superadmin specific
    "/settings"       # Superadmin specific
)

echo "FALLBACK screens (${#FALLBACK_SCREENS[@]}): ${FALLBACK_SCREENS[*]}"
echo "ACTUAL accessible screens (${#ACCESSIBLE_SCREENS[@]}): ${ACCESSIBLE_SCREENS[*]}"

echo ""
echo "📊 COMPARISON:"
echo "Fallback count: ${#FALLBACK_SCREENS[@]}"
echo "Actual count: ${#ACCESSIBLE_SCREENS[@]}"

# Check if fallback matches actual
MISSING_IN_FALLBACK=()
for screen in "${ACCESSIBLE_SCREENS[@]}"; do
    if [[ ! " ${FALLBACK_SCREENS[*]} " =~ " $screen " ]]; then
        MISSING_IN_FALLBACK+=("$screen")
    fi
done

EXTRA_IN_FALLBACK=()
for screen in "${FALLBACK_SCREENS[@]}"; do
    if [[ ! " ${ACCESSIBLE_SCREENS[*]} " =~ " $screen " ]]; then
        EXTRA_IN_FALLBACK+=("$screen")
    fi
done

echo ""
echo "🚨 ISSUES FOUND:"
if [[ ${#MISSING_IN_FALLBACK[@]} -gt 0 ]]; then
    echo "Missing in fallback: ${MISSING_IN_FALLBACK[*]}"
fi

if [[ ${#EXTRA_IN_FALLBACK[@]} -gt 0 ]]; then
    echo "Extra in fallback: ${EXTRA_IN_FALLBACK[*]}"
fi

if [[ ${#MISSING_IN_FALLBACK[@]} -eq 0 && ${#EXTRA_IN_FALLBACK[@]} -eq 0 ]]; then
    echo "✅ Fallback matches actual permissions!"
else
    echo ""
    echo "💡 ROOT CAUSE: Fallback logic doesn't match actual permissions!"
    echo "   This causes menu to show different items during loading vs after loading"
    echo "   The user perceives this as 'menu disappearing' when it actually changes"
fi

# Step 6: Check frontend is running
echo ""
echo "6. Testing frontend availability..."
curl -s "http://localhost:3000" > /dev/null
if [[ $? -eq 0 ]]; then
    echo "✅ Frontend is running at http://localhost:3000"
    echo "   Try opening http://localhost:3000/dashboard in browser"
    echo "   Watch the Network tab for API calls during login"
else
    echo "❌ Frontend is NOT running at http://localhost:3000"
    echo "   Run: cd frontend && npm start"
fi

echo ""
echo "🎯 CONCLUSION:"
if [[ ${#MISSING_IN_FALLBACK[@]} -gt 0 || ${#EXTRA_IN_FALLBACK[@]} -gt 0 ]]; then
    echo "The menu disappears because fallback logic ≠ actual permissions"
    echo "Fix: Update NavBar.tsx fallback logic to match actual API permissions"
else
    echo "Fallback logic matches API permissions - issue might be elsewhere"
    echo "Check browser console for JavaScript errors"
fi