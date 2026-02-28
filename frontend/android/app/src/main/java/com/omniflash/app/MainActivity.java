package com.omniflash.app;

import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;
import androidx.core.content.ContextCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // ensure system bars match theme
        Window w = getWindow();
        w.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        w.setStatusBarColor(ContextCompat.getColor(this, R.color.colorPrimaryDark));
        w.setNavigationBarColor(ContextCompat.getColor(this, R.color.colorPrimaryDark));
    }
}
