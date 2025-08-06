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


    private static string ReadAsciiZ(byte[] data, int offset, int maxLength)
    {
        int end = Array.IndexOf<byte>(data, 0, offset, maxLength);
        if (end < 0) end = offset + maxLength;
        return Encoding.ASCII.GetString(data, offset, end - offset);
    }

    public string name
    {
        get { return ReadAsciiZ(data, 12, 16); }
    }

    public string version
    {
        get { return ReadAsciiZ(data, 28, 24); }
    }

    public string sn
    {
        get { return ReadAsciiZ(data, 52, 24); }
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
                Console.WriteLine("===================");
                Console.WriteLine("RBL name: " + rbl.name);
                Console.WriteLine("RBL ver: " + rbl.version);
                Console.WriteLine("RBL sn: " + rbl.sn);
                Console.WriteLine("RBL size_package: " + rbl.size_package);
                Console.WriteLine("RBL size_raw: " + rbl.size_raw);
                Console.WriteLine("RBL time " + rbl.timestampDT);
                rbl.setFullData(input, i);
                list.Add(rbl);
            }
        }
        return list;
    }

    private void setFullData(byte[] input, int ofs)
    {
        int rem_size = input.Length - ofs;
        if(rem_size < this.size_package)
        {
            Console.WriteLine("Not enough size to extract! Wants " + size_package + " has " + rem_size+"");
            return;
        }
        uint saveSize = size_package;
        data = new byte[saveSize];
        Array.Copy(input, ofs, data, 0, saveSize);

    }
}


