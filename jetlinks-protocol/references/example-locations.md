# Example Locations

## Support registration and transport binding

- Search for `*ProtocolSupportProvider`, `CompositeProtocolSupport`, `addMessageCodecSupport`, `addAuthenticator`, `addRoutes`, and `setDocument`.
- These files usually reveal which transports are supported, which docs belong to each transport, and where to start tracing a codec.

## Transport codecs and routing helpers

- Search for `*DeviceMessageCodec`, `*TopicMessageCodec`, `*TopicHandler`, `HttpRoute`, and `WebsocketRoute`.
- Look for config metadata definitions near the codec so auth keys, secure keys, and transport-specific settings stay aligned.

## Binary protocol core

- Search for `BinaryMessageType`, `DataType`, `AckCode`, `Binary*Message`, or any packet registry that converts between bytes and `DeviceMessage`.
- Use these files to understand framing, type codes, dynamic field parsing, and reply correlation.

## Protocol docs and packet examples

- Look for root `README.md`, `binary-protocol.md`, and `src/main/resources/document-*.md`.
- Use these files to locate the intended packet contract, then compare with the target device/version and code. A code/document mismatch needs resolution; the existing implementation alone does not establish the correct wire protocol.

## Tests

- Search for `*Binary*Test`, `*Topic*Test`, and codec-specific tests before adding new coverage.
- Prefer extending an existing round-trip or route test instead of adding isolated demo code.
