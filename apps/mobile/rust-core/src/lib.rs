use jni::JNIEnv;
use jni::objects::{JClass, JString};
use jni::sys::{jstring, jboolean};

#[no_mangle]
pub extern "system" fn Java_com_sheralganesh_mobile_RustCore_initP2P(
    mut env: JNIEnv,
    _class: JClass,
    input: JString,
) -> jstring {
    let peer_id: String = env.get_string(&input).expect("Couldn't get java string!").into();
    // Simulate initializing a libp2p node
    let output = env.new_string(format!("Rust P2P initialized for peer: {}", peer_id)).expect("Couldn't create java string!");
    output.into_raw()
}

#[no_mangle]
pub extern "system" fn Java_com_sheralganesh_mobile_RustCore_startNode(
    mut _env: JNIEnv,
    _class: JClass,
) -> jboolean {
    // Simulate starting the libp2p node
    println!("libp2p node started");
    1 // true
}

#[no_mangle]
pub extern "system" fn Java_com_sheralganesh_mobile_RustCore_stopNode(
    mut _env: JNIEnv,
    _class: JClass,
) -> jboolean {
    // Simulate stopping the libp2p node
    println!("libp2p node stopped");
    1 // true
}
