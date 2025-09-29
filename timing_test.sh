#!/bin/bash
# Simple timing test for API responses

echo "🕐 API Response Timing Test"
echo "========================="

BASE_URL="http://localhost:8001/api/v1"

# Get token first
echo "Getting authentication token..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=superadmin&password=superadmin123")

TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [[ -z "$TOKEN" ]]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Token received"
echo ""

# Test permission API timing
echo "Testing permission API response times..."
for i in {1..5}; do
    echo -n "Test $i: "
    START=$(python3 -c "import time; print(int(time.time() * 1000))")
    curl -s "$BASE_URL/screen-permissions/check?screen_route=/dashboard&action=view" \
        -H "Authorization: Bearer $TOKEN" > /dev/null
    END=$(python3 -c "import time; print(int(time.time() * 1000))")
    DURATION=$((END - START))
    echo "${DURATION}ms"
done

echo ""
echo "🔍 Analysis Summary:"
echo "- Fallback shows: 8 menu items"
echo "- Actual shows: 16 menu items"  
echo "- When permissions load, menu DOUBLES in size"
echo "- This sudden change may appear as 'disappearing' if there's a rendering issue"