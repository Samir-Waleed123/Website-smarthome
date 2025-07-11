# Railway Deployment Guide for Smart Home MQTT

## Environment Variables Required

Set these environment variables in your Railway project:

### Required Variables
```
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
DATABASE_URI=your_postgresql_connection_string
MQTT_BROKER=your_mqtt_broker_host
MQTT_PORT=1883
MQTT_USER=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password
```

### Optional Variables (for Railway optimization)
```
MQTT_USE_TLS=false
MQTT_KEEPALIVE=60
```

## Common MQTT Issues on Railway

### 1. **Connection Timeouts**
- Railway has stricter timeout limits
- Use shorter keepalive intervals (60 seconds instead of 6000)
- Set `MQTT_KEEPALIVE=60`

### 2. **TLS/SSL Issues**
- Railway may block certain TLS configurations
- Try setting `MQTT_USE_TLS=false` if you have connection issues
- Use port 1883 for non-TLS or 8883 for TLS

### 3. **Network Restrictions**
- Railway containers have limited outbound connections
- Ensure your MQTT broker allows connections from Railway's IP ranges
- Consider using a public MQTT broker for testing

## Testing MQTT Connection

1. **Check MQTT Status**: Visit `/api/mqtt-status` (requires authentication)
2. **Monitor Logs**: Check Railway logs for MQTT connection messages
3. **Test Topics**: Ensure your MQTT broker is publishing to the expected topics

## Recommended MQTT Brokers for Railway

### Public Brokers (for testing)
- **test.mosquitto.org**: `MQTT_BROKER=test.mosquitto.org`, `MQTT_PORT=1883`
- **broker.hivemq.com**: `MQTT_BROKER=broker.hivemq.com`, `MQTT_PORT=1883`

### Cloud Brokers
- **AWS IoT Core**: Requires proper certificate setup
- **Azure IoT Hub**: Requires proper authentication
- **Google Cloud IoT**: Requires proper authentication

## Troubleshooting

### If MQTT doesn't connect:
1. Check Railway logs for connection errors
2. Verify environment variables are set correctly
3. Try disabling TLS: `MQTT_USE_TLS=false`
4. Use a public broker for testing
5. Check if your MQTT broker allows external connections

### If device status doesn't update:
1. Verify MQTT topics match exactly
2. Check if the MQTT client is receiving messages
3. Ensure the polling mechanism is working
4. Check browser console for JavaScript errors

## Alternative Solutions

If MQTT continues to fail on Railway:

1. **WebSocket Fallback**: Implement WebSocket connections as an alternative
2. **REST API Polling**: Increase polling frequency for real-time updates
3. **Server-Sent Events**: Use SSE for real-time updates
4. **External MQTT Service**: Use a cloud MQTT service that's Railway-compatible 