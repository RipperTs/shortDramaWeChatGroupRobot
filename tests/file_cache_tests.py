from diskcache import Cache

# 创建缓存
cache = Cache('./cache')

# 设置带过期时间的缓存
# cache.set('access_token', 'token-value', expire=7200)  # 过期时间为秒

# 获取缓存
token = cache.get('access_token')

print(token)