using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace InformationCamp
{
    public class ValidatorServiceProvider
    {
        // 驗證資料是否存在SQL常見關鍵字，以避免 SQL Injection的發生
        public bool SqlInjectionTryParse(System.Web.UI.Page myPage, string val, string fieldname, bool isRequired)
        {
            var isValid = true;

            if (isRequired)
            {
                if (val.Length == 0)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('未輸入 [" + fieldname + "] 欄位之資料，請輸入！');</script>");

                    return false;
                }
            }

            // 取消 or 與 and 兩個常用的字
            // string[] filter1 = new string[] { "select", "insert", "update", "delete", "script", "or", "and" };
            string[] filter1 = new string[] { "select", "insert", "update", "delete", "script"};

            System.Text.RegularExpressions.Regex re = null;
            bool isGetKeyWord = false;

            for (int i = 0; i < filter1.Length; i++)
            {
                // 寫程式的時候要注意替 \b 加上 @
                re = new System.Text.RegularExpressions.Regex(@"\b" + filter1[i] + @"\b", System.Text.RegularExpressions.RegexOptions.Singleline | System.Text.RegularExpressions.RegexOptions.IgnoreCase);
                isGetKeyWord = re.IsMatch(val);

                if (isGetKeyWord)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料格式不正確，請重新輸入！');</script>");
                    isValid = false;
                    break;
                }
            }

            return isValid;
        }

        // 驗證資料是否符合電子郵件的格式
        public bool EmailTryParse(System.Web.UI.Page myPage, string val, string fieldname, bool isRequired)
        {
            var isValid = true;

            if (isRequired)
            {
                if (val.Length == 0)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('未輸入 [" + fieldname + "] 欄位之資料，請輸入！');</script>");

                    return false;
                }
            }

            if (System.Text.RegularExpressions.Regex.IsMatch(val, @"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$"))
            {
                isValid = true;
            }
            else
            {
                myPage.ClientScript.RegisterStartupScript(this.GetType(),
                                "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料格式不正確，請重新確認！');</script>");
                return false;
            }

            return isValid;
        }

        // 驗證資料是否為整數（含最小值與最大值之檢測）
        public bool IntegerTryParse(System.Web.UI.Page myPage, string val, string fieldname, int minvalue, long maxvalue, bool isRequired)
        {
            var isValid = true;
            long intOutResult = 0;

            if (isRequired)
            {
                if (val.Length == 0)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('未輸入 [" + fieldname + "] 欄位之資料，請重新確認！');</script>");

                    return false;
                }
            }

            isValid = Int64.TryParse(val, out intOutResult);

            if (isValid)
            {
                if (intOutResult < minvalue)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料應大於或等於 [" + minvalue.ToString() + "]，請重新確認！');</script>");

                    return false;
                }
                else if (intOutResult > maxvalue)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料應小於或等於 [" + maxvalue.ToString() + "]，請重新確認！');</script>");

                    return false;
                }
            }
            else
            {
                myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料格式不正確，請重新確認！');</script>");

                return false;
            }

            return isValid;
        }

        // Source:http://blog.yam.com/csylvia/article/21713029
        // 驗證資料是否超過長度限制（含中文，每個中文代表2 Bytes）
        public bool ChineseTryParse(System.Web.UI.Page myPage, string val, string fieldname, int minvalue, int maxvalue, bool isRequired)
        {
            int totalCharCount = 0;

            for (int i = 0; i < val.Length; i++)
            {
                char _c = val[i]; // var[i] 代表 JavaScript 裡面的 val.charCodeAt(i)

                if (_c <= 0x7f)
                {
                    totalCharCount++;
                }
                else
                {
                    totalCharCount += 2;
                }
            }

            if (isRequired)
            {
                if (val.Length == 0)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                                "showMsg", "<script>alert('未輸入 [" + fieldname + "] 欄位之資料，請重新確認！');</script>");
                    return false;
                }
            }

            if (totalCharCount < minvalue)
            {
                myPage.ClientScript.RegisterStartupScript(this.GetType(),
                            "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料小於長度限制 [" + Convert.ToString(minvalue) + "個字元]，請重新確認！');</script>");
                return false;
            }

            if (totalCharCount > maxvalue)
            {
                myPage.ClientScript.RegisterStartupScript(this.GetType(),
                            "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料超過長度限制 [" + Convert.ToString(maxvalue) + "個字元]，請重新確認！');</script>");
                return false;
            }

            return true;
        }

        public bool FloatTryParse(System.Web.UI.Page myPage, string val, string fieldname, int minvalue, int maxvalue, bool isRequired)
        {
            var isValid = true;
            decimal decOutResult = 0;

            if (isRequired)
            {
                if (val.Length == 0)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('未輸入 [" + fieldname + "] 欄位之資料，請重新確認！');</script>");

                    return false;
                }
            }

            // 驗證文字的最後一碼是否為點(.) 
            char endch = val.Where((item, index) => index == val.Length - 1).Single();
            
            if (endch == '.')
            {
                myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料格式不正確，請重新輸入！');</script>");
                
                return false;
            }

            // 驗證第一碼是否為 0
            endch = val.Where((item, index) => index == 0).Single();

            if (endch == '0')
            {
                myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料格式不正確，請重新輸入！');</script>");

                return false;
            }

            int HavePoints = 0;
            int PointsIndex = 0;
            for (var i = 0; i < val.Length; i++)
            {
                char ch = val.Where((item, index) => index == i).Single();
                if (ch == '.')
                {
                    HavePoints += 1;
                    PointsIndex = i;
                    if (HavePoints > 1)
                    {
                        myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料格式不正確，請重新輸入！');</script>");
                        return false;
                    }
                }
                else if (ch < '0' || ch > '9')
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料格式不正確，請重新輸入！');</script>");
                    return false;
                }
            }

            decOutResult = Convert.ToDecimal(val);

            if (isValid)
            {
                if (decOutResult < minvalue)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料應大於或等於 [" + minvalue.ToString() + "]，請重新確認！');</script>");

                    return false;
                }
                else if (decOutResult > maxvalue)
                {
                    myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料應小於或等於 [" + maxvalue.ToString() + "]，請重新確認！');</script>");

                    return false;
                }
            }
            else
            {
                myPage.ClientScript.RegisterStartupScript(this.GetType(),
                        "showMsg", "<script>alert('[" + fieldname + "] 欄位之資料格式不正確，請重新確認！');</script>");

                return false;
            }

            return isValid;
        }
    }
}