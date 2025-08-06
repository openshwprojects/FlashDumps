using System;
using System.Collections.Generic;
using System.Text;

[Flags]
public enum OTAAlgorithm
{
    NONE = 0,
    CRYPT_XOR = 1,
    CRYPT_AES256 = 2,
    COMPRESS_GZIP = 256,
    COMPRESS_QUICKLZ = 512,
    COMPRESS_FASTLZ = 768
}

public class RBL
{
    public byte[] data;

    public RBL(byte[] data)
    {
        this.data = data;
    }

    public string magic
    {
        get { return Encoding.ASCII.GetString(data, 0, 4); }
    }

    public OTAAlgorithm algo
    {
        get { return (OTAAlgorithm)BitConverter.ToUInt32(data, 4); }
    }

    public int timestamp
    {
        get { return BitConverter.ToInt32(data, 8); }
    }

    public DateTime timestampDT
    {
        get
        {
            return DateTimeOffset.FromUnixTimeSeconds(timestamp).DateTime;
        }
    }



    public string name
    {
        get { return Encoding.ASCII.GetString(data, 12, 16).TrimEnd('\0'); }
    }

    public string version
    {
        get { return Encoding.ASCII.GetString(data, 28, 24).TrimEnd('\0'); }
    }

    public string sn
    {
        get { return Encoding.ASCII.GetString(data, 52, 24).TrimEnd('\0'); }
    }

    public uint crc32
    {
        get { return BitConverter.ToUInt32(data, 76); }
    }

    public uint hash
    {
        get { return BitConverter.ToUInt32(data, 80); }
    }

    public uint size_raw
    {
        get { return BitConverter.ToUInt32(data, 84); }
    }

    public uint size_package
    {
        get { return BitConverter.ToUInt32(data, 88); }
    }

    public uint info_crc32
    {
        get { return BitConverter.ToUInt32(data, 92); }
    }



    public static readonly byte[] MAGIC = Encoding.ASCII.GetBytes("RBL\0");
    public const int SIZE = 96;

    public static List<RBL> findIn(byte[] input)
    {
        List<RBL> list = new List<RBL>();
        for (int i = 0; i <= input.Length - SIZE; i++)
        {
            if (input[i] == MAGIC[0] && input[i + 1] == MAGIC[1] && input[i + 2] == MAGIC[2] && input[i + 3] == MAGIC[3])
            {
                byte[] block = new byte[SIZE];
                Array.Copy(input, i, block, 0, SIZE);
                RBL rbl = new RBL(block);
                Console.WriteLine("RBL time " + rbl.timestampDT);
                list.Add(rbl);
            }
        }
        return list;
    }

}


