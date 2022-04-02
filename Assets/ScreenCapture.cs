using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Windows;

public class ScreenCapture : MonoBehaviour
{
    [SerializeField]
    private Communication communication;

    private bool willTakeScreenShot = true;
    private bool print = true;
    private Camera camera;
    [SerializeField]
    private GameObject target;

    private float start;
    private int count = 0;

    // Start is called before the first frame update
    void Start()
    {
        camera = GetComponent<Camera>();
    }

    // Update is called once per frame
    void Update()
    {
        if(count == 0)
            start = Time.time;

        if (Time.time - start > 1)
        {
            //Debug.Log(count +" "+ start+" "  +Time.time);
            count = 0;
        }
        else 
        {
            count++;
        }


        if (communication.data.Length > 3 && communication.isFirst)
        {
            communication.isFirst = false;
            string[] datas = communication.data.Split(' ');
            Debug.Log(datas);
            float depth = float.Parse(datas[2]);
            float z = 220.67126f * depth - 9.96772f;

            float x = float.Parse(datas[0]);
            float y = float.Parse(datas[1]);


            Vector3 tempPos = camera.ViewportToWorldPoint(new Vector3(x / 1920f, (1080f - y) / 1080f, z + 10f));
            //Vector3 tempPos1 = camera.ViewportToWorldPoint(new Vector3(0f, 1f, 5f));
            //Vector3 tempPos2 = camera.ViewportToWorldPoint(new Vector3(0f, 0f, 5f));
            //Vector3 tempPos3 = camera.ViewportToWorldPoint(new Vector3(1f, 0f, 5f));


            //float x = tempPos2.x + (tempPos3.x - tempPos2.x) * 986.0f / 1920f;
            //float y = tempPos2.y + (tempPos1.y - tempPos2.y) * (1080f - 552.75f) / 1080f;


            target.transform.position = new Vector3(tempPos.x, tempPos.y, tempPos.z);
        }
    }

    IEnumerator ScreenShot()
    {
        Texture2D screenTexture = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);

        Rect area = new Rect(0f, 0f, Screen.width, Screen.height);
        screenTexture.ReadPixels(area, 0, 0);
        screenTexture.Apply();

        Color[] screenPixels = screenTexture.GetPixels();

        string pixelString = "";
        pixelString += (int)(screenPixels[10][0] * 255);

        File.WriteAllBytes($"{Application.dataPath}/Python/img.png", screenTexture.EncodeToPNG());

        communication.imageUpdated = true;

        yield return new WaitForSeconds(1.0f);

        willTakeScreenShot = true;

        yield return null;
    }

    private void OnPostRender()
    {  
        if (willTakeScreenShot)
        {        
            StartCoroutine(ScreenShot());

            willTakeScreenShot = false;
        }

        
    }
}
