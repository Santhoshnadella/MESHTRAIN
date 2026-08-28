package com.meshtrain.mobile;

import com.facebook.react.bridge.NativeModule;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import java.util.Map;
import java.util.HashMap;

public class RustCoreModule extends ReactContextBaseJavaModule {
    RustCoreModule(ReactApplicationContext context) {
        super(context);
    }

    @Override
    public String getName() {
        return "RustCoreModule";
    }

    // Load the Rust library
    static {
        System.loadLibrary("meshcoin_mobile_core");
    }

    // Declare the native method implemented in Rust
    private native String initP2P(String input);

    @ReactMethod
    public void startNode(String peerId) {
        String result = initP2P(peerId);
        System.out.println("Rust node started: " + result);
    }
}
