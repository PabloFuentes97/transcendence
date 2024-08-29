

export async function checkTwoFactorAuthStatus() {
    const enableSection = document.getElementById('enableTwoFactorAuthSection');
    const disableSection = document.getElementById('disableTwoFactorAuthSection');
    const twoFactorTitle = document.getElementById('enableTwoFactorTitle');
    const settingsSecuritySection = document.getElementById('settingsSecuritySection');
    const settingsSecurityTittle = document.getElementById('settingsSecurityTittle');
    const qrCodeContainer = document.getElementById('qrCodeContainer');
    
    try {
        const token = localStorage.getItem('jwtToken');

        const response_from_intra = await fetch('/auth_service/is_from_intra/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        if (!response_from_intra.ok) throw new Error('Failed to fetch is from intra');
        const data_from_intra = await response_from_intra.json();
        
        if (data_from_intra.from_intra)
        {
            twoFactorTitle.style.display = 'none';
            disableSection.style.display = 'none';
            enableSection.style.display = 'none';
            settingsSecuritySection.style.display = 'none';
            settingsSecurityTittle.style.display = 'none';

        }
        else
        {
            const response = await fetch('/auth_service/is_2fa_enabled/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to fetch 2FA status');
            const data = await response.json();

            if (data.is_2fa_enabled) {
                disableSection.style.display = 'block';
                enableSection.style.display = 'none';
                document.getElementById('disableTwoFactorButton').addEventListener('click', disableTwoFactorAuth);
                
            } else {
                disableSection.style.display = 'none';
                enableSection.style.display = 'block';
                document.getElementById('enableTwoFactorButton').addEventListener('click', enableTwoFactorAuth);
                QRCode.toCanvas(qrCodeContainer, data.uri, function (error) {
                    if (error) console.error('Error generating QR code:', error);
                });
                
            }
        }
        } catch (error) {
            console.error('Error checking 2FA status:', error);
        }
}

export async function enableTwoFactorAuth() {
    const code_2fa = document.getElementById('enableTwoFactorCode');
    const failInfoEnable2FA = document.getElementById("failInfoEnable2FA");
    try {
        const token = localStorage.getItem('jwtToken');
        const response = await fetch('/auth_service/enable_2fa/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code_2fa: code_2fa.value })
        });
        code_2fa.value = "";
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error);
        }
        document.getElementById('enableTwoFactorAuthSection').style.display = 'none';
        document.getElementById('disableTwoFactorAuthSection').style.display = 'block';
        document.getElementById('disableTwoFactorButton').addEventListener('click', disableTwoFactorAuth);
    } catch (error) {
        failInfoEnable2FA.textContent = error.message;
    }
}

export async function disableTwoFactorAuth() {
    const code_2fa = document.getElementById('disableTwoFactorCode');
    const failInfoDisable2FA = document.getElementById("failInfoDisable2FA");
    try {
        const token = localStorage.getItem('jwtToken');
        const response = await fetch('/auth_service/disable_2fa/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code_2fa: code_2fa.value })
        });
        code_2fa.value = "";
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error);
        }
        checkTwoFactorAuthStatus();
    } catch (error) {
        failInfoDisable2FA.textContent = error.message;
    }
}
