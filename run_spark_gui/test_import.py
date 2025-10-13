"""Test import modules"""
import traceback

try:
    from system_utils import cache_manager, timed, RetryHandler
    print('✅ system_utils imported successfully')
    print(f'   cache_manager: {cache_manager}')
    print(f'   timed decorator: {timed}')
    print(f'   RetryHandler: {RetryHandler}')
except Exception as e:
    print(f'❌ ERROR importing system_utils: {e}')
    traceback.print_exc()

try:
    from database import db
    print('✅ database imported successfully')
    print(f'   db: {db}')
except Exception as e:
    print(f'❌ ERROR importing database: {e}')
    traceback.print_exc()

# Now test spark_backend
try:
    from spark_backend import ENHANCED_FEATURES, get_container_status
    print(f'✅ spark_backend imported')
    print(f'   ENHANCED_FEATURES: {ENHANCED_FEATURES}')
except Exception as e:
    print(f'❌ ERROR importing spark_backend: {e}')
    traceback.print_exc()
